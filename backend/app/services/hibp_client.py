"""Cliente HIBP con rate limiting, retry exponencial y caché Redis."""
import asyncio
import hashlib
import json
import logging
import time
from typing import Any

import httpx
import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)


class HIBPError(Exception):
    pass


class HIBPClient:
    def __init__(self, redis_client: aioredis.Redis | None = None):
        self.base_url = settings.HIBP_BASE_URL
        self.headers = {
            "hibp-api-key": settings.HIBP_API_KEY.get_secret_value(),
            "user-agent": settings.HIBP_USER_AGENT,
        }
        self.rate_limit = settings.HIBP_RATE_LIMIT_SECONDS
        self.max_retries = settings.HIBP_MAX_RETRIES
        self.backoff_base = settings.HIBP_BACKOFF_BASE
        self.redis = redis_client
        self._last_call = 0.0
        self._lock = asyncio.Lock()

    async def _throttle(self) -> None:
        async with self._lock:
            elapsed = time.monotonic() - self._last_call
            if elapsed < self.rate_limit:
                await asyncio.sleep(self.rate_limit - elapsed)
            self._last_call = time.monotonic()

    def _cache_key(self, endpoint: str, param: str) -> str:
        return "hibp:" + hashlib.sha256(f"{endpoint}|{param}".encode()).hexdigest()

    async def _get_cached(self, key: str) -> Any | None:
        if not self.redis:
            return None
        raw = await self.redis.get(key)
        return json.loads(raw) if raw else None

    async def _set_cache(self, key: str, value: Any) -> None:
        if not self.redis:
            return
        await self.redis.setex(
            key, settings.HIBP_CACHE_TTL_HOURS * 3600, json.dumps(value, default=str)
        )

    async def _request(self, path: str, param: str) -> Any | None:
        cache_key = self._cache_key(path, param)
        cached = await self._get_cached(cache_key)
        if cached is not None:
            logger.debug("HIBP cache hit %s", cache_key)
            return cached

        url = f"{self.base_url}{path}"
        for attempt in range(1, self.max_retries + 1):
            await self._throttle()
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    resp = await client.get(url, headers=self.headers)
                if resp.status_code == 200:
                    data = resp.json()
                    await self._set_cache(cache_key, data)
                    return data
                if resp.status_code == 404:
                    await self._set_cache(cache_key, [])
                    return []
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("retry-after", 5))
                    logger.warning("HIBP 429, esperando %ss", retry_after)
                    await asyncio.sleep(retry_after)
                    continue
                if 500 <= resp.status_code < 600:
                    raise HIBPError(f"HIBP {resp.status_code}")
                raise HIBPError(f"HIBP status inesperado {resp.status_code}")
            except (httpx.HTTPError, HIBPError) as exc:
                backoff = self.backoff_base ** attempt
                logger.warning("HIBP intento %s falló (%s), backoff %.1fs", attempt, exc, backoff)
                if attempt == self.max_retries:
                    raise HIBPError(f"HIBP agotó reintentos: {exc}") from exc
                await asyncio.sleep(backoff)
        return None

    async def breached_domain(self, domain: str) -> dict[str, list[str]]:
        """Devuelve {email: [breach_names]}. Requiere plan pago HIBP."""
        data = await self._request(f"/breacheddomain/{domain}", domain)
        return data or {}

    async def breached_account(self, email: str) -> list[dict]:
        """Plan gratuito: consulta por cuenta."""
        data = await self._request(f"/breachedaccount/{email}", email)
        return data or []

    async def all_breaches(self) -> list[dict]:
        """Catálogo de breaches (para enriquecer severidad)."""
        return await self._request("/breaches", "all") or []

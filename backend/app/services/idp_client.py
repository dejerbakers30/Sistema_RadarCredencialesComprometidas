"""Adaptador multi-IdP: Entra ID, Google Workspace, LDAP, webhook genérico."""
import hashlib
import hmac
import json
import logging
from abc import ABC, abstractmethod

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class IdPResult:
    def __init__(self, ok: bool, detail: dict | None = None, error: str | None = None):
        self.ok = ok
        self.detail = detail or {}
        self.error = error


class BaseIdP(ABC):
    @abstractmethod
    async def reset_password(self, email: str) -> IdPResult: ...

    @abstractmethod
    async def revoke_sessions(self, email: str) -> IdPResult: ...


class GenericWebhookIdP(BaseIdP):
    """Envía un webhook firmado HMAC-SHA256 al IAM receptor."""

    def __init__(self, url: str, secret: str):
        self.url = url
        self.secret = secret.encode()

    def _sign(self, body: bytes) -> str:
        return hmac.new(self.secret, body, hashlib.sha256).hexdigest()

    async def _post(self, action: str, email: str) -> IdPResult:
        payload = {"action": action, "email": email}
        body = json.dumps(payload).encode()
        headers = {
            "Content-Type": "application/json",
            "X-Radar-Signature": self._sign(body),
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(self.url, content=body, headers=headers)
            if resp.status_code in (200, 202):
                return IdPResult(True, detail={"status": resp.status_code})
            return IdPResult(False, error=f"HTTP {resp.status_code}: {resp.text[:200]}")
        except httpx.HTTPError as exc:
            return IdPResult(False, error=str(exc))

    async def reset_password(self, email: str) -> IdPResult:
        return await self._post("reset_password", email)

    async def revoke_sessions(self, email: str) -> IdPResult:
        return await self._post("revoke_sessions", email)


class EntraIdP(BaseIdP):
    """Microsoft Graph: reset password + revokeSignInSessions."""

    def __init__(self, tenant: str, client_id: str, client_secret: str):
        self.tenant = tenant
        self.client_id = client_id
        self.client_secret = client_secret

    async def _token(self) -> str:
        url = f"https://login.microsoftonline.com/{self.tenant}/oauth2/v2.0/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, data=data)
        resp.raise_for_status()
        return resp.json()["access_token"]

    async def _user_id(self, token: str, email: str) -> str | None:
        url = f"https://graph.microsoft.com/v1.0/users/{email}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers={"Authorization": f"Bearer {token}"})
        if resp.status_code == 200:
            return resp.json()["id"]
        return None

    async def reset_password(self, email: str) -> IdPResult:
        try:
            token = await self._token()
            uid = await self._user_id(token, email)
            if not uid:
                return IdPResult(False, error="Usuario no encontrado en Entra")
            url = f"https://graph.microsoft.com/v1.0/users/{uid}/authentication/methods/resetPassword"
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(url, headers={"Authorization": f"Bearer {token}"})
            if resp.status_code in (200, 204):
                return IdPResult(True, detail={"user_id": uid})
            return IdPResult(False, error=f"HTTP {resp.status_code}")
        except Exception as exc:  # noqa: BLE001
            return IdPResult(False, error=str(exc))

    async def revoke_sessions(self, email: str) -> IdPResult:
        try:
            token = await self._token()
            uid = await self._user_id(token, email)
            if not uid:
                return IdPResult(False, error="Usuario no encontrado en Entra")
            url = f"https://graph.microsoft.com/v1.0/users/{uid}/revokeSignInSessions"
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(url, headers={"Authorization": f"Bearer {token}"})
            if resp.status_code in (200, 204):
                return IdPResult(True, detail={"user_id": uid})
            return IdPResult(False, error=f"HTTP {resp.status_code}")
        except Exception as exc:  # noqa: BLE001
            return IdPResult(False, error=str(exc))


class LDAPIdP(BaseIdP):
    """LDAP: fuerza cambio de contraseña marcando pwdReset=TRUE."""

    def __init__(self, server: str, base_dn: str, bind_dn: str, bind_password: str):
        self.server = server
        self.base_dn = base_dn
        self.bind_dn = bind_dn
        self.bind_password = bind_password

    def _sync_reset(self, email: str) -> IdPResult:
        # Import diferido para no exigir ldap3 si no se usa
        from ldap3 import ALL, Connection, Server, MODIFY_REPLACE

        server = Server(self.server, get_info=ALL)
        conn = Connection(server, self.bind_dn, self.bind_password, auto_bind=True)
        search_filter = f"(mail={email})"
        conn.search(self.base_dn, search_filter, attributes=["distinguishedName"])
        if not conn.entries:
            conn.unbind()
            return IdPResult(False, error="Usuario no encontrado en LDAP")
        dn = conn.entries[0].distinguishedName.value
        conn.modify(dn, {"pwdReset": [(MODIFY_REPLACE, ["TRUE"])]})
        ok = conn.result["result"] == 0
        conn.unbind()
        return IdPResult(ok, detail={"dn": dn}, error=None if ok else str(conn.result))

    async def reset_password(self, email: str) -> IdPResult:
        import asyncio
        return await asyncio.to_thread(self._sync_reset, email)

    async def revoke_sessions(self, email: str) -> IdPResult:
        # LDAP no gestiona sesiones; se delega a otro sistema (Kerberos ticket purge).
        return IdPResult(True, detail={"nota": "revocación de sesiones delegada"})


def build_idp() -> BaseIdP:
    provider = settings.IDP_PROVIDER
    if provider == "entra":
        return EntraIdP(
            settings.IDP_TENANT_ID,
            settings.IDP_CLIENT_ID,
            settings.IDP_CLIENT_SECRET.get_secret_value(),
        )
    if provider == "ldap":
        return LDAPIdP(
            settings.LDAP_SERVER,
            settings.LDAP_BASE_DN,
            settings.LDAP_BIND_DN,
            settings.LDAP_BIND_PASSWORD.get_secret_value(),
        )
    # generic_webhook (Google Workspace y otros se implementan como webhook propio)
    return GenericWebhookIdP(
        settings.IDP_WEBHOOK_URL,
        settings.IDP_WEBHOOK_HMAC_SECRET.get_secret_value(),
    )

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import pyotp
import hashlib
import os
import base64
import hmac
from jose import JWTError, jwt

from app.core.config import settings

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return base64.b64encode(salt + key).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    try:
        data = base64.b64decode(hashed.encode('utf-8'))
        salt = data[:16]
        stored_key = data[16:]
        new_key = hashlib.pbkdf2_hmac('sha256', plain.encode(), salt, 100000)
        return new_key == stored_key
    except Exception:
        return False


def create_access_token(subject: str, rol: str, token_version: int = 0,
                        extra: dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "rol": rol,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
        "type": "access",
        "token_version": token_version,
        **(extra or {}),
    }
    return jwt.encode(payload, settings.JWT_SECRET.get_secret_value(), algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str, token_version: int = 0) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()),
        "type": "refresh",
        "token_version": token_version,
    }
    return jwt.encode(payload, settings.JWT_SECRET.get_secret_value(), algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token, settings.JWT_SECRET.get_secret_value(), algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError as exc:
        raise ValueError(f"Token inválido: {exc}") from exc


def generate_mfa_secret() -> str:
    return pyotp.random_base32()


def verify_mfa(secret: str, code: str) -> bool:
    return pyotp.TOTP(secret).verify(code, valid_window=1)


def hash_challenge(challenge: str) -> str:
    return hashlib.sha256(challenge.encode("utf-8")).hexdigest()


def compare_challenge(challenge: str, expected_hash: str) -> bool:
    return hmac.compare_digest(hash_challenge(challenge), expected_hash)


def is_challenge_valid(challenge: str, expected_hash: str | None,
                       expires_at: datetime | None, now: datetime | None = None) -> bool:
    current = now or datetime.now(timezone.utc)
    return bool(expected_hash and expires_at and expires_at > current
                and compare_challenge(challenge, expected_hash))

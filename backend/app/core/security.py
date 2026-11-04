from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import pyotp
import hashlib
import os
import base64
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


def create_access_token(subject: str, rol: str, extra: dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "rol": rol,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
        "type": "access",
        **(extra or {}),
    }
    return jwt.encode(payload, settings.JWT_SECRET.get_secret_value(), algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()),
        "type": "refresh",
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

"""Cifrado simétrico para secretos en reposo (MFA secrets, tokens)."""
import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings


def _key() -> bytes:
    # Derivar clave de 32 bytes desde JWT_SECRET (en prod: KMS/Vault)
    raw = settings.JWT_SECRET.get_secret_value().encode()
    return raw[:32].ljust(32, b"0")


def encrypt(plaintext: str) -> str:
    aes = AESGCM(_key())
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ct).decode()


def decrypt(token: str) -> str:
    data = base64.b64decode(token)
    nonce, ct = data[:12], data[12:]
    aes = AESGCM(_key())
    return aes.decrypt(nonce, ct, None).decode()

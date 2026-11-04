from datetime import datetime, timezone
from typing import Annotated

import pyotp

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import client_meta, get_current_user
from app.core.crypto import encrypt, decrypt
from app.core.security import (
    create_access_token, create_refresh_token, decode_token,
    hash_password, verify_mfa, verify_password, generate_mfa_secret,
)
from app.db.models.user import Role, Usuario
from app.db.session import get_db
from app.schemas.auth import LoginRequest, MFAVerifyRequest, RefreshRequest, TokenResponse
from app.schemas.auth import MfaEnrollResponse, MfaVerifyEnrollRequest
from app.services.audit import write_audit

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    user = db.execute(select(Usuario).where(Usuario.email == payload.email)).scalar_one_or_none()
    meta = client_meta(request)
    if not user or not user.activo or not user.password_hash or not verify_password(payload.password, user.password_hash):
        write_audit(db, modulo="auth", accion="login", resultado="denied",
                    usuario_email=payload.email, ip_origen=meta.get("ip"), user_agent=meta.get("user_agent"))
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales inválidas")

    if user.mfa_enabled:
        write_audit(db, modulo="auth", accion="login_mfa_pending", resultado="ok",
                    usuario_email=user.email, ip_origen=meta.get("ip"), user_agent=meta.get("user_agent"))
        return TokenResponse(
            access_token="", refresh_token="", expires_in=0, mfa_required=True
        )

    user.ultimo_login = datetime.now(timezone.utc)
    access = create_access_token(str(user.id), user.rol.nombre)
    refresh = create_refresh_token(str(user.id))
    write_audit(db, modulo="auth", accion="login", resultado="ok",
                usuario_email=user.email, ip_origen=meta.get("ip"), user_agent=meta.get("user_agent"))
    return TokenResponse(
        access_token=access, refresh_token=refresh,
        expires_in=30 * 60,
    )


@router.post("/mfa/verify", response_model=TokenResponse)
def mfa_verify(
    payload: MFAVerifyRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    user = db.execute(select(Usuario).where(Usuario.email == payload.email)).scalar_one_or_none()
    meta = client_meta(request)
    if not user or not user.mfa_secret or not verify_mfa(user.mfa_secret, payload.code):
        write_audit(db, modulo="auth", accion="mfa_verify", resultado="denied",
                    usuario_email=payload.email, ip_origen=meta.get("ip"), user_agent=meta.get("user_agent"))
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Código MFA inválido")
    user.ultimo_login = datetime.now(timezone.utc)
    access = create_access_token(str(user.id), user.rol.nombre)
    refresh = create_refresh_token(str(user.id))
    write_audit(db, modulo="auth", accion="mfa_verify", resultado="ok",
                usuario_email=user.email, ip_origen=meta.get("ip"), user_agent=meta.get("user_agent"))
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=30 * 60)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshRequest, db: Annotated[Session, Depends(get_db)]):
    try:
        data = decode_token(payload.refresh_token)
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh inválido")
    if data.get("type") != "refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Tipo incorrecto")
    user = db.get(Usuario, data["sub"])
    if not user or not user.activo:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario inválido")
    access = create_access_token(str(user.id), user.rol.nombre)
    new_refresh = create_refresh_token(str(user.id))
    return TokenResponse(access_token=access, refresh_token=new_refresh, expires_in=30 * 60)


@router.get("/me")
def me(user: Annotated[Usuario, Depends(get_current_user)]):
    return {"id": str(user.id), "email": user.email, "nombre": user.nombre,
            "rol": user.rol.nombre, "mfa_enabled": user.mfa_enabled}


@router.post("/mfa/enroll", response_model=MfaEnrollResponse)
def mfa_enroll(
    user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Genera un secreto TOTP y lo guarda cifrado. No activa MFA hasta verificar."""
    if user.mfa_enabled:
        raise HTTPException(status.HTTP_409_CONFLICT, "MFA ya está activado")
    secret = generate_mfa_secret()
    user.mfa_secret = encrypt(secret)
    db.flush()
    otpauth_url = pyotp.TOTP(secret).provisioning_uri(
        name=user.email, issuer_name="RadarCreds"
    )
    write_audit(
        db, modulo="auth", accion="mfa_enroll_init",
        resultado="ok", usuario_id=user.id, usuario_email=user.email,
    )
    return MfaEnrollResponse(secret=secret, otpauth_url=otpauth_url)


@router.post("/mfa/verify-enroll")
def mfa_verify_enroll(
    payload: MfaVerifyEnrollRequest,
    user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Verifica el primer código y activa MFA de forma definitiva."""
    if user.mfa_enabled:
        raise HTTPException(status.HTTP_409_CONFLICT, "MFA ya está activado")
    if not user.mfa_secret:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Primero solicita /mfa/enroll")
    secret = decrypt(user.mfa_secret)
    if not verify_mfa(secret, payload.code):
        write_audit(
            db, modulo="auth", accion="mfa_verify_enroll",
            resultado="denied", usuario_id=user.id, usuario_email=user.email,
        )
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Código MFA inválido")
    user.mfa_enabled = True
    db.flush()
    write_audit(
        db, modulo="auth", accion="mfa_verify_enroll",
        resultado="ok", usuario_id=user.id, usuario_email=user.email,
    )
    return {"ok": True, "mfa_enabled": True}

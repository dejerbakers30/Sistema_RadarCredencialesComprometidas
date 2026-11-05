from typing import Annotated
from uuid import UUID

import hmac

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.rbac import load_role_permissions
from app.core.config import settings
from app.core.security import decode_token
from app.db.models.user import Role, Usuario
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario:
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido")
    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Tipo de token incorrecto")
    sub = payload.get("sub")
    try:
        user_id = UUID(sub)
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido")
    user = db.execute(select(Usuario).where(Usuario.id == user_id)).scalar_one_or_none()
    if not user or not user.activo:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario inactivo o inexistente")
    if payload.get("token_version", 0) != user.token_version:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sesión revocada")
    return user


def require_permission(modulo: str, accion: str):
    def _checker(
        user: Annotated[Usuario, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_db)],
    ) -> Usuario:
        if (modulo, accion) not in load_role_permissions(db, user.rol.nombre):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Rol '{user.rol.nombre}' sin permiso {modulo}:{accion}",
            )
        return user

    return _checker


def require_permission_or_service(modulo: str, accion: str):
    """Allow a normal RBAC user or the configured n8n service token."""
    def _checker(
        authorization: str | None = Header(default=None),
        token: str | None = Depends(OAuth2PasswordBearer(
            tokenUrl="/api/v1/auth/login", auto_error=False
        )),
        db: Session = Depends(get_db),
    ) -> Usuario:
        configured = settings.N8N_SERVICE_TOKEN
        if (
            configured is not None
            and authorization
            and authorization.startswith("Bearer ")
            and hmac.compare_digest(
                authorization.removeprefix("Bearer "), configured.get_secret_value()
            )
        ):
            service_user = db.execute(
                select(Usuario).where(Usuario.activo.is_(True)).order_by(Usuario.email)
            ).scalars().first()
            if service_user and (modulo, accion) in load_role_permissions(
                db, service_user.rol.nombre
            ):
                return service_user
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Servicio sin permisos suficientes")
        if not token:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Autenticación requerida")
        user = get_current_user(token, db)
        if (modulo, accion) not in load_role_permissions(db, user.rol.nombre):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Rol '{user.rol.nombre}' sin permiso {modulo}:{accion}",
            )
        return user

    return _checker


def client_meta(request: Request) -> dict:
    return {
        "ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }

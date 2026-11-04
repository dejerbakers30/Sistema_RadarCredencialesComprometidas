from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.rbac import has_permission
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
    user = db.execute(select(Usuario).where(Usuario.id == UUID(sub))).scalar_one_or_none()
    if not user or not user.activo:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario inactivo o inexistente")
    return user


def require_permission(modulo: str, accion: str):
    def _checker(user: Annotated[Usuario, Depends(get_current_user)]) -> Usuario:
        if not has_permission(user.rol.nombre, modulo, accion):
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

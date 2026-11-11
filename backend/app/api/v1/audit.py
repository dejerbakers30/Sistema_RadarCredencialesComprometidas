# audit.py
import hmac
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, oauth2_scheme, require_permission
from app.core.rbac import load_role_permissions
from app.core.config import settings
from app.db.models.audit import AuditLog
from app.db.models.user import Usuario
from app.db.session import get_db
from app.schemas.audit import AuditLogRead, AuditLogWrite
from app.services.audit import verify_chain, write_audit

router = APIRouter(prefix="/audit", tags=["audit"])


def require_n8n_service_token(authorization: str | None = Header(default=None)) -> None:
    configured = settings.N8N_SERVICE_TOKEN
    if configured is None or not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Autenticación de servicio requerida")
    supplied = authorization.removeprefix("Bearer ")
    if not hmac.compare_digest(supplied, configured.get_secret_value()):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token de servicio inválido")


def require_verify_access(
    authorization: str | None = Header(default=None),
    token: Annotated[str, Depends(oauth2_scheme)] = "",
    db: Session = Depends(get_db),
) -> None:
    """Allow the n8n service token or the existing RBAC user contract."""
    configured = settings.N8N_SERVICE_TOKEN
    if (
        configured is not None
        and authorization
        and authorization.startswith("Bearer ")
        and hmac.compare_digest(
            authorization.removeprefix("Bearer "), configured.get_secret_value()
        )
    ):
        return

    user = get_current_user(token, db)
    if ("audit", "read") not in load_role_permissions(db, user.rol.nombre):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"Rol '{user.rol.nombre}' sin permiso audit:read",
        )


@router.post("/internal", response_model=AuditLogRead, status_code=status.HTTP_201_CREATED)
def write_internal_audit(
    payload: AuditLogWrite,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(require_n8n_service_token)],
):
    """Registra auditoría desde un orquestador confiable usando la lógica canónica."""
    return write_audit(db, **payload.model_dump())


@router.get("", response_model=list[AuditLogRead])
def list_audit(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(require_permission("audit", "read"))],
    modulo: str | None = None,
    desde: datetime | None = None,
    hasta: datetime | None = None,
    limit: int = Query(200, le=1000),
):
    q = select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)
    if modulo:
        q = q.where(AuditLog.modulo == modulo)
    if desde:
        q = q.where(AuditLog.ts >= desde)
    if hasta:
        q = q.where(AuditLog.ts <= hasta)
    return db.execute(q).scalars().all()


@router.get("/verify")
def verify(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(require_verify_access)],
):
    return verify_chain(db)

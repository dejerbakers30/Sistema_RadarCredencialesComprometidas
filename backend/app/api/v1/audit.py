# audit.py
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import require_permission
from app.db.models.audit import AuditLog
from app.db.models.user import Usuario
from app.db.session import get_db
from app.schemas.audit import AuditLogRead
from app.services.audit import verify_chain

router = APIRouter(prefix="/audit", tags=["audit"])


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
    _: Annotated[Usuario, Depends(require_permission("audit", "read"))],
):
    return verify_chain(db)

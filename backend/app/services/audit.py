"""Escritura y verificación de cadena de auditoría."""
import hashlib
import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.audit import AuditLog

logger = logging.getLogger(__name__)


def _compute_hash(
    ts: str, usuario_email: str | None, modulo: str, accion: str, resultado: str, prev: str
) -> str:
    payload = f"{ts}|{usuario_email or ''}|{modulo}|{accion}|{resultado}|{prev}"
    return hashlib.sha256(payload.encode()).hexdigest()


def write_audit(
    db: Session,
    *,
    modulo: str,
    accion: str,
    resultado: str,
    entidad: str | None = None,
    entidad_id: str | None = None,
    usuario_id: UUID | None = None,
    usuario_email: str | None = None,
    ip_origen: str | None = None,
    user_agent: str | None = None,
    detalle: dict | None = None,
    tz: str | None = None,
) -> AuditLog:
    prev = db.execute(select(AuditLog.hash_actual).order_by(AuditLog.id.desc()).limit(1)).scalar()
    prev = prev or "GENESIS"
    ts = datetime.now(timezone.utc)
    ts_iso = ts.isoformat()
    h = _compute_hash(ts_iso, usuario_email, modulo, accion, resultado, prev)
    entry = AuditLog(
        ts=ts,
        tz=tz or settings.TIMEZONE,
        usuario_id=str(usuario_id) if usuario_id else None,
        usuario_email=usuario_email,
        modulo=modulo,
        accion=accion,
        entidad=entidad,
        entidad_id=entidad_id,
        resultado=resultado,
        ip_origen=ip_origen,
        user_agent=user_agent,
        detalle=detalle,
        hash_anterior=prev,
        hash_actual=h,
    )
    db.add(entry)
    db.flush()
    return entry


def verify_chain(db: Session, limit: int | None = None) -> dict:
    """Recalcula hashes y detecta manipulaciones."""
    q = select(AuditLog).order_by(AuditLog.id.asc())
    if limit:
        q = q.limit(limit)
    rows = db.execute(q).scalars().all()
    prev = "GENESIS"
    broken: list[int] = []
    for r in rows:
        expected_prev = prev
        expected = _compute_hash(
            r.ts.isoformat(), r.usuario_email, r.modulo, r.accion, r.resultado, expected_prev
        )
        if r.hash_anterior != expected_prev or r.hash_actual != expected:
            broken.append(r.id)
        prev = r.hash_actual
    return {"total": len(rows), "broken": broken, "ok": not broken}

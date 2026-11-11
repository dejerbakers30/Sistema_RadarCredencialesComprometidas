"""Escritura y verificación de cadena de auditoría."""
import hashlib
import ipaddress
import json
import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.audit import AuditLog

logger = logging.getLogger(__name__)


def normalize_ip(value: object | None) -> str | None:
    """Return a canonical IP string, ignoring symbolic test/proxy hosts."""
    if not value:
        return None
    try:
        if isinstance(value, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            return str(value)
        return str(ipaddress.ip_address(str(value).strip()))
    except ValueError:
        return None


def _canonical_datetime(value: datetime) -> str:
    aware = value if value.tzinfo else value.replace(tzinfo=UTC)
    return aware.astimezone(UTC).isoformat(timespec="microseconds")


def _canonical_audit_payload(
    *,
    ts: datetime,
    tz: str | None,
    usuario_id: str | None,
    usuario_email: str | None,
    modulo: str,
    accion: str,
    entidad: str | None,
    entidad_id: str | None,
    resultado: str,
    ip_origen: str | None,
    user_agent: str | None,
    detalle: dict | None,
    hash_anterior: str,
) -> bytes:
    payload = {
        "ts": _canonical_datetime(ts),
        "tz": tz,
        "usuario_id": usuario_id,
        "usuario_email": usuario_email,
        "modulo": modulo,
        "accion": accion,
        "entidad": entidad,
        "entidad_id": entidad_id,
        "resultado": resultado,
        "ip_origen": normalize_ip(ip_origen),
        "user_agent": user_agent,
        "detalle": detalle,
        "hash_anterior": hash_anterior,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def compute_audit_hash(entry: AuditLog, hash_anterior: str) -> str:
    payload = _canonical_audit_payload(
        ts=entry.ts,
        tz=entry.tz,
        usuario_id=entry.usuario_id,
        usuario_email=entry.usuario_email,
        modulo=entry.modulo,
        accion=entry.accion,
        entidad=entry.entidad,
        entidad_id=entry.entidad_id,
        resultado=entry.resultado,
        ip_origen=entry.ip_origen,
        user_agent=entry.user_agent,
        detalle=entry.detalle,
        hash_anterior=hash_anterior,
    )
    return hashlib.sha256(payload).hexdigest()


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
    db.execute(text("SELECT pg_advisory_xact_lock(hashtextextended('radar:audit_log_chain', 0))"))
    prev = db.execute(select(AuditLog.hash_actual).order_by(AuditLog.id.desc()).limit(1)).scalar()
    prev = prev or "GENESIS"
    ts = datetime.now(UTC)
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
        ip_origen=normalize_ip(ip_origen),
        user_agent=user_agent,
        detalle=detalle,
        hash_anterior=prev,
        hash_actual="pending",
    )
    entry.hash_actual = compute_audit_hash(entry, prev)
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
        expected = compute_audit_hash(r, expected_prev)
        if r.hash_anterior != expected_prev or r.hash_actual != expected:
            broken.append(r.id)
        prev = r.hash_actual
    return {"total": len(rows), "broken": broken, "ok": not broken}

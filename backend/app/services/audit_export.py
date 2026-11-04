"""Exporta auditoría a CSV firmado para entrega a auditores."""
import csv
import hashlib
import hmac
import io
import os
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.audit import AuditLog


def export_audit_csv(db: Session, desde: datetime, hasta: datetime) -> tuple[str, str, str]:
    rows = db.execute(
        select(AuditLog).where(AuditLog.ts >= desde, AuditLog.ts <= hasta).order_by(AuditLog.id)
    ).scalars().all()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "ts", "tz", "usuario_email", "modulo", "accion",
                     "entidad", "entidad_id", "resultado", "hash_anterior", "hash_actual"])
    for r in rows:
        writer.writerow([r.id, r.ts.isoformat(), r.tz, r.usuario_email, r.modulo, r.accion,
                         r.entidad, r.entidad_id, r.resultado, r.hash_anterior, r.hash_actual])
    content = buf.getvalue().encode()
    os.makedirs(settings.REPORTS_STORAGE_PATH, exist_ok=True)
    nombre = f"audit_{desde.date()}_{hasta.date()}.csv"
    path = os.path.join(settings.REPORTS_STORAGE_PATH, nombre)
    with open(path, "wb") as f:
        f.write(content)
    digest = hashlib.sha256(content).hexdigest()
    signature = hmac.new(
        settings.JWT_SECRET.get_secret_value().encode(), content, hashlib.sha256
    ).hexdigest()
    return path, digest, signature

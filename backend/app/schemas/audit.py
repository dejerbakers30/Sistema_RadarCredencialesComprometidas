# audit.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ts: datetime
    tz: str
    usuario_email: str | None
    modulo: str
    accion: str
    entidad: str | None
    entidad_id: str | None
    resultado: str
    detalle: dict | None
    hash_actual: str


class AuditLogWrite(BaseModel):
    modulo: str
    accion: str
    resultado: str
    entidad: str | None = None
    entidad_id: str | None = None
    usuario_id: UUID | None = None
    usuario_email: str | None = None
    ip_origen: str | None = None
    user_agent: str | None = None
    detalle: dict | None = None

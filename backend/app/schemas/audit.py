# audit.py
from datetime import datetime
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

# reset.py
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.db.models.reset import ResetMetodo, ResetResultado


class ResetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    leak_hit_id: UUID
    usuario_ejecutor: UUID | None
    timestamp: datetime
    metodo: ResetMetodo
    resultado: ResetResultado
    intentos: int
    proximo_intento: datetime | None
    error_detalle: str | None


class ResetManualRequest(BaseModel):
    leak_hit_id: UUID
    motivo: str | None = None

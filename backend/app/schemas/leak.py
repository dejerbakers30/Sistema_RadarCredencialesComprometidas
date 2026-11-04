from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.db.models.leak import LeakEstado, LeakSeveridad


class LeakHitBase(BaseModel):
    email_corporativo: EmailStr
    breach_origen: str
    breach_dominio: str | None = None
    fecha_breach: date | None = None
    severidad: LeakSeveridad = LeakSeveridad.media
    fuente_detalle: str | None = None
    datos_expuestos: list[str] | None = None


class LeakHitCreate(LeakHitBase):
    fuente_id: int
    hash_canonico: str


class LeakHitRead(LeakHitBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    usuario_id: UUID | None
    fecha_deteccion: datetime
    estado: LeakEstado
    fecha_contencion: datetime | None
    hash_canonico: str


class LeakHitUpdate(BaseModel):
    estado: LeakEstado | None = None
    severidad: LeakSeveridad | None = None
    usuario_id: UUID | None = None

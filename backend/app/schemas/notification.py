from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    leak_hit_id: UUID | None
    destinatario: str
    canal: str
    plantilla: str | None
    enviado_en: datetime | None
    estado: str
    error_detalle: str | None


class NotificationPage(BaseModel):
    items: list[NotificationRead]
    total: int
    limit: int
    offset: int

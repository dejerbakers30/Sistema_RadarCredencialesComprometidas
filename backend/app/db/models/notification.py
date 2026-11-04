# notification.py
from datetime import datetime
from uuid import UUID
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, UUIDPKMixin


class Notificacion(Base, UUIDPKMixin):
    __tablename__ = "notificaciones"
    leak_hit_id: Mapped[UUID | None] = mapped_column(ForeignKey("leak_hits.id", ondelete="CASCADE"))
    destinatario: Mapped[str] = mapped_column(CITEXT, nullable=False)
    canal: Mapped[str] = mapped_column(String(20), nullable=False)
    plantilla: Mapped[str | None] = mapped_column(String(50))
    enviado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    estado: Mapped[str] = mapped_column(String(20), default="pendiente", nullable=False)
    error_detalle: Mapped[str | None] = mapped_column(Text)

import enum
from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class LeakEstado(str, enum.Enum):
    nuevo = "nuevo"
    contenido = "contenido"
    resuelto = "resuelto"
    falso_positivo = "falso_positivo"


class LeakSeveridad(str, enum.Enum):
    baja = "baja"
    media = "media"
    alta = "alta"
    critica = "critica"


class LeakHit(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "leak_hits"
    email_corporativo: Mapped[str] = mapped_column(CITEXT, nullable=False, index=True)
    usuario_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), index=True
    )
    breach_origen: Mapped[str] = mapped_column(String(200), nullable=False)
    breach_dominio: Mapped[str | None] = mapped_column(String(200))
    fecha_breach: Mapped[date | None] = mapped_column(Date)
    fecha_deteccion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    severidad: Mapped[LeakSeveridad] = mapped_column(
        Enum(LeakSeveridad, name="leak_severidad"), default=LeakSeveridad.media, nullable=False
    )
    fuente_id: Mapped[int] = mapped_column(ForeignKey("fuentes.id"), nullable=False)
    fuente_detalle: Mapped[str | None] = mapped_column(String(200))
    datos_expuestos: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    estado: Mapped[LeakEstado] = mapped_column(
        Enum(LeakEstado, name="leak_estado"), default=LeakEstado.nuevo, nullable=False, index=True
    )
    fecha_contencion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    hash_canonico: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    resets: Mapped[list["Reset"]] = relationship(back_populates="leak_hit")  # noqa: F821

    __table_args__ = (
        Index("idx_leak_fecha_det_desc", fecha_deteccion.desc()),
    )

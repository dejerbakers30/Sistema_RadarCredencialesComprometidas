import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Index, SmallInteger, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPKMixin


class ResetMetodo(str, enum.Enum):
    automatico = "automatico"
    manual = "manual"


class ResetResultado(str, enum.Enum):
    exitoso = "exitoso"
    fallido = "fallido"
    pendiente = "pendiente"
    reintento = "reintento"


class Reset(Base, UUIDPKMixin):
    __tablename__ = "resets"
    leak_hit_id: Mapped[UUID] = mapped_column(
        ForeignKey("leak_hits.id", ondelete="CASCADE"), nullable=False, index=True
    )
    usuario_ejecutor: Mapped[UUID | None] = mapped_column(ForeignKey("usuarios.id"))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    metodo: Mapped[ResetMetodo] = mapped_column(Enum(ResetMetodo, name="reset_metodo"), nullable=False)
    resultado: Mapped[ResetResultado] = mapped_column(
        Enum(ResetResultado, name="reset_resultado"), default=ResetResultado.pendiente, nullable=False
    )
    idp_respuesta: Mapped[dict | None] = mapped_column(JSONB)
    intentos: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)
    proximo_intento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    error_detalle: Mapped[str | None] = mapped_column(Text)

    leak_hit: Mapped["LeakHit"] = relationship(back_populates="resets")  # noqa: F821

    __table_args__ = (
        Index("idx_resets_pendientes", "resultado", "proximo_intento",
              postgresql_where="resultado IN ('pendiente','reintento')"),
    )

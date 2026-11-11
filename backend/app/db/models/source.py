# source.py
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Fuente(Base):
    __tablename__ = "fuentes"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    endpoint: Mapped[str | None] = mapped_column(Text)
    api_key_ref: Mapped[str | None] = mapped_column(String(200))
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rate_limit_rps: Mapped[float] = mapped_column(Numeric(6, 2), default=0.5)
    ultima_consulta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class DominioMonitoreado(Base):
    __tablename__ = "dominios_monitoreados"
    id: Mapped[int] = mapped_column(primary_key=True)
    dominio: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    organizacion: Mapped[str | None] = mapped_column(String(200))
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    verificado_hibp: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

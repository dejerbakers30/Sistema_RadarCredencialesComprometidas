# report.py
from datetime import date, datetime
from uuid import UUID
from sqlalchemy import Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, UUIDPKMixin


class Report(Base, UUIDPKMixin):
    __tablename__ = "reports"
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    formato: Mapped[str] = mapped_column(String(10), nullable=False)
    periodo_desde: Mapped[date] = mapped_column(Date, nullable=False)
    periodo_hasta: Mapped[date] = mapped_column(Date, nullable=False)
    generado_por: Mapped[UUID | None] = mapped_column(ForeignKey("usuarios.id"))
    generado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ruta_archivo: Mapped[str] = mapped_column(String(500), nullable=False)
    hash_archivo: Mapped[str] = mapped_column(String(64), nullable=False)

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import CITEXT, INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    tz: Mapped[str] = mapped_column(String(50), nullable=False, default="UTC")
    usuario_id: Mapped[str | None] = mapped_column(String(36))
    usuario_email: Mapped[str | None] = mapped_column(CITEXT)
    modulo: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    accion: Mapped[str] = mapped_column(String(50), nullable=False)
    entidad: Mapped[str | None] = mapped_column(String(50))
    entidad_id: Mapped[str | None] = mapped_column(String(64))
    resultado: Mapped[str] = mapped_column(String(20), nullable=False)
    ip_origen: Mapped[str | None] = mapped_column(INET)
    user_agent: Mapped[str | None] = mapped_column(Text)
    detalle: Mapped[dict | None] = mapped_column(JSONB)
    hash_anterior: Mapped[str | None] = mapped_column(String(64))
    hash_actual: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        Index("idx_audit_modulo_ts", "modulo", "ts"),
        Index("idx_audit_usuario_ts", "usuario_email", "ts"),
    )

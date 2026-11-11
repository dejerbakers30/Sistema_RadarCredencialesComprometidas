from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)

    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="rol")
    permisos: Mapped[list["Permiso"]] = relationship(
        secondary="rol_permisos", back_populates="roles"
    )


class Permiso(Base):
    __tablename__ = "permisos"
    id: Mapped[int] = mapped_column(primary_key=True)
    modulo: Mapped[str] = mapped_column(String(50), nullable=False)
    accion: Mapped[str] = mapped_column(String(50), nullable=False)

    roles: Mapped[list[Role]] = relationship(
        secondary="rol_permisos", back_populates="permisos"
    )


class RolPermiso(Base):
    __tablename__ = "rol_permisos"
    rol_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permiso_id: Mapped[int] = mapped_column(
        ForeignKey("permisos.id", ondelete="CASCADE"), primary_key=True
    )


class Usuario(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "usuarios"
    email: Mapped[str] = mapped_column(CITEXT, unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    rol_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False, index=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    idp_subject: Mapped[str | None] = mapped_column(String(255))
    password_hash: Mapped[str | None] = mapped_column(String(255))  # solo si auth local
    mfa_secret: Mapped[str | None] = mapped_column(String(255))
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_challenge_hash: Mapped[str | None] = mapped_column(String(64))
    mfa_challenge_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    token_version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ultimo_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    rol: Mapped[Role] = relationship(back_populates="usuarios")

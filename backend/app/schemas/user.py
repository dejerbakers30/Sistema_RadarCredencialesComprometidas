from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    nombre: str
    rol: str
    password: str | None = Field(None, min_length=12)


class UserUpdate(BaseModel):
    nombre: str | None = None
    rol: str | None = None
    activo: bool | None = None
    password: str | None = Field(None, min_length=12)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: EmailStr
    nombre: str
    activo: bool
    mfa_enabled: bool

from pydantic import BaseModel


class RolePermissionRead(BaseModel):
    modulo: str
    accion: str


class RoleRead(BaseModel):
    id: int
    nombre: str
    descripcion: str | None
    permisos: list[RolePermissionRead]
    usuarios: list[str]

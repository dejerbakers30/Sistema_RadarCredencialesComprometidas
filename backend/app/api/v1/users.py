from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.security import hash_password
from app.db.models.user import Role, Usuario
from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.audit import write_audit

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(require_permission("users", "read"))],
):
    return db.execute(select(Usuario)).scalars().all()


@router.post("", response_model=UserRead)
def create_user(
    payload: UserCreate,
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[Usuario, Depends(require_permission("users", "write"))],
):
    if db.execute(select(Usuario).where(Usuario.email == payload.email)).scalar_one_or_none():
        raise HTTPException(409, "Email ya registrado")
    rol = db.execute(select(Role).where(Role.nombre == payload.rol)).scalar_one_or_none()
    if not rol:
        raise HTTPException(400, "Rol inexistente")
    u = Usuario(
        email=payload.email, nombre=payload.nombre, rol_id=rol.id,
        password_hash=hash_password(payload.password) if payload.password else None,
    )
    db.add(u)
    db.flush()
    write_audit(db, modulo="admin", accion="user_create", resultado="ok",
                entidad="usuarios", entidad_id=str(u.id),
                usuario_id=actor.id, usuario_email=actor.email)
    return u


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: str, payload: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[Usuario, Depends(require_permission("users", "write"))],
):
    u = db.get(Usuario, user_id)
    if not u:
        raise HTTPException(404, "Usuario no encontrado")
    for k, v in payload.model_dump(exclude_unset=True).items():
        if k == "rol":
            rol = db.execute(select(Role).where(Role.nombre == v)).scalar_one_or_none()
            if not rol:
                raise HTTPException(400, "Rol inexistente")
            u.rol_id = rol.id
        elif k == "password":
            u.password_hash = hash_password(v)
        else:
            setattr(u, k, v)
    db.flush()
    write_audit(db, modulo="admin", accion="user_update", resultado="ok",
                entidad="usuarios", entidad_id=str(u.id),
                usuario_id=actor.id, usuario_email=actor.email)
    return u

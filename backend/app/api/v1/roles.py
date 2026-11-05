from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import require_permission
from app.db.models.user import Role, Usuario
from app.db.session import get_db
from app.schemas.role import RoleRead

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=list[RoleRead])
def list_roles(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(require_permission("roles", "read"))],
):
    roles = db.execute(
        select(Role).options(selectinload(Role.permisos), selectinload(Role.usuarios))
        .order_by(Role.id)
    ).scalars().unique().all()
    return [
        {
            "id": role.id,
            "nombre": role.nombre,
            "descripcion": role.descripcion,
            "permisos": [{"modulo": p.modulo, "accion": p.accion} for p in role.permisos],
            "usuarios": [u.email for u in role.usuarios],
        }
        for role in roles
    ]

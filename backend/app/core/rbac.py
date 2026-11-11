"""RBAC: resolución de permisos efectivos por rol, cacheable en Redis."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.user import Permiso, Role, RolPermiso


def load_role_permissions(db: Session, rol_nombre: str) -> set[tuple[str, str]]:
    """Carga permisos efectivos desde la base de datos."""
    stmt = (
        select(Permiso.modulo, Permiso.accion)
        .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
        .join(Role, Role.id == RolPermiso.rol_id)
        .where(Role.nombre == rol_nombre)
    )
    rows = db.execute(stmt).all()
    return {(m, a) for m, a in rows}

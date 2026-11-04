"""RBAC: resolución de permisos efectivos por rol, cacheable en Redis."""
from functools import lru_cache

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.user import Permiso, Role, RolPermiso

# Matriz base (se siembra en migración; aquí como fallback documental)
DEFAULT_MATRIX: dict[str, set[tuple[str, str]]] = {
    "admin": {
        ("dashboard", "read"), ("leaks", "read"), ("leaks", "write"), ("leaks", "export"),
        ("resets", "read"), ("resets", "execute"), ("reports", "read"), ("reports", "generate"),
        ("reports", "schedule"), ("users", "read"), ("users", "write"), ("users", "admin"),
        ("roles", "read"), ("roles", "write"), ("audit", "read"), ("audit", "export"),
        ("sources", "read"), ("sources", "write"), ("config", "admin"),
    },
    "soc_analyst": {
        ("dashboard", "read"), ("leaks", "read"), ("leaks", "write"), ("leaks", "export"),
        ("resets", "read"), ("resets", "execute"), ("reports", "read"), ("reports", "generate"),
        ("audit", "read"), ("sources", "read"),
    },
    "auditor": {
        ("dashboard", "read"), ("leaks", "read"), ("leaks", "export"),
        ("resets", "read"), ("reports", "read"), ("reports", "generate"),
        ("audit", "read"), ("audit", "export"), ("users", "read"),
    },
    "end_user": {
        ("dashboard", "read"), ("notifications", "read"), ("profile", "write"),
    },
}


def load_role_permissions(db: Session, rol_nombre: str) -> set[tuple[str, str]]:
    """Carga permisos desde BD; si no existen, usa la matriz por defecto."""
    stmt = (
        select(Permiso.modulo, Permiso.accion)
        .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
        .join(Role, Role.id == RolPermiso.rol_id)
        .where(Role.nombre == rol_nombre)
    )
    rows = db.execute(stmt).all()
    if rows:
        return {(m, a) for m, a in rows}
    return DEFAULT_MATRIX.get(rol_nombre, set())


@lru_cache(maxsize=64)
def _cached_matrix(rol_nombre: str) -> frozenset[tuple[str, str]]:
    return frozenset(DEFAULT_MATRIX.get(rol_nombre, set()))


def has_permission(rol_nombre: str, modulo: str, accion: str) -> bool:
    return (modulo, accion) in _cached_matrix(rol_nombre)

# sources.py
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import require_permission
from app.db.models.source import DominioMonitoreado, Fuente
from app.db.models.user import Usuario
from app.db.session import get_db

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("")
def list_sources(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(require_permission("sources", "read"))],
):
    fuentes = db.execute(select(Fuente)).scalars().all()
    dominios = db.execute(select(DominioMonitoreado)).scalars().all()
    return {
        "fuentes": [{"id": f.id, "nombre": f.nombre, "activa": f.activa,
                     "ultima_consulta": f.ultima_consulta} for f in fuentes],
        "dominios": [{"id": d.id, "dominio": d.dominio, "activo": d.activo} for d in dominios],
    }

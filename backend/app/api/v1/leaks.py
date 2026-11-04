from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.models.leak import LeakEstado, LeakHit
from app.db.models.user import Usuario
from app.db.session import get_db
from app.schemas.leak import LeakHitRead, LeakHitUpdate

router = APIRouter(prefix="/leaks", tags=["leaks"])


@router.get("", response_model=list[LeakHitRead])
def list_leaks(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(require_permission("leaks", "read"))],
    estado: LeakEstado | None = None,
    email: str | None = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
):
    q = select(LeakHit).order_by(LeakHit.fecha_deteccion.desc()).limit(limit).offset(offset)
    if estado:
        q = q.where(LeakHit.estado == estado)
    if email:
        q = q.where(LeakHit.email_corporativo == email)
    return db.execute(q).scalars().all()


@router.get("/kpis")
def kpis(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(require_permission("dashboard", "read"))],
):
    total = db.execute(select(func.count(LeakHit.id))).scalar() or 0
    nuevos = db.execute(
        select(func.count(LeakHit.id)).where(LeakHit.estado == LeakEstado.nuevo)
    ).scalar() or 0
    contenidos = db.execute(
        select(func.count(LeakHit.id)).where(LeakHit.estado == LeakEstado.contenido)
    ).scalar() or 0
    mttc = db.execute(
        select(func.avg(func.extract("epoch", LeakHit.fecha_contencion - LeakHit.fecha_deteccion)) / 60)
        .where(LeakHit.fecha_contencion.isnot(None))
    ).scalar()
    return {
        "total": total, "nuevos": nuevos, "contenidos": contenidos,
        "mttc_min": float(mttc) if mttc else None,
    }


@router.patch("/{leak_id}", response_model=LeakHitRead)
def update_leak(
    leak_id: str,
    payload: LeakHitUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[Usuario, Depends(require_permission("leaks", "write"))],
):
    hit = db.get(LeakHit, leak_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(hit, field, value)
    db.flush()
    return hit

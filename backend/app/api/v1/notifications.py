from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.models.notification import Notificacion
from app.db.models.user import Usuario
from app.db.session import get_db
from app.schemas.notification import NotificationPage

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationPage)
def list_notifications(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[Usuario, Depends(require_permission("notifications", "read"))],
    estado: str | None = None,
    canal: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = select(Notificacion)
    count_query = select(func.count(Notificacion.id))
    if user.rol.nombre not in {"admin", "soc_analyst", "auditor"}:
        query = query.where(Notificacion.destinatario == user.email)
        count_query = count_query.where(Notificacion.destinatario == user.email)
    if estado:
        query = query.where(Notificacion.estado == estado)
        count_query = count_query.where(Notificacion.estado == estado)
    if canal:
        query = query.where(Notificacion.canal == canal)
        count_query = count_query.where(Notificacion.canal == canal)
    total = db.execute(count_query).scalar_one()
    items = db.execute(
        query.order_by(Notificacion.enviado_en.desc().nullslast(), Notificacion.id.desc())
        .limit(limit).offset(offset)
    ).scalars().all()
    return {"items": items, "total": total, "limit": limit, "offset": offset}

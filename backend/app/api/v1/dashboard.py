# dashboard.py
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.deps import require_permission
from app.db.models.leak import LeakEstado, LeakHit, LeakSeveridad
from app.db.models.reset import Reset, ResetResultado
from app.db.models.user import Usuario
from app.db.session import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(require_permission("dashboard", "read"))],
    dias: int = 30,
):
    desde = datetime.now(timezone.utc) - timedelta(days=dias)
    dia_deteccion = func.date_trunc("day", LeakHit.fecha_deteccion)
    por_dia = db.execute(
        select(dia_deteccion, func.count(LeakHit.id))
        .where(LeakHit.fecha_deteccion >= desde)
        .group_by(dia_deteccion)
        .order_by(dia_deteccion)
    ).all()
    por_sev = db.execute(
        select(LeakHit.severidad, func.count(LeakHit.id)).group_by(LeakHit.severidad)
    ).all()
    top_breaches = db.execute(
        select(LeakHit.breach_origen, func.count(LeakHit.id))
        .group_by(LeakHit.breach_origen).order_by(func.count(LeakHit.id).desc()).limit(10)
    ).all()
    resets_estado = db.execute(
        select(Reset.resultado, func.count(Reset.id)).group_by(Reset.resultado)
    ).all()
    reincidentes = db.execute(
        select(LeakHit.email_corporativo, func.count(LeakHit.id))
        .group_by(LeakHit.email_corporativo).having(func.count(LeakHit.id) > 1)
        .order_by(func.count(LeakHit.id).desc()).limit(20)
    ).all()
    return {
        "tendencia_diaria": [{"fecha": str(f), "total": c} for f, c in por_dia],
        "por_severidad": [{"severidad": s.value, "total": c} for s, c in por_sev],
        "top_breaches": [{"breach": b, "total": c} for b, c in top_breaches],
        "resets_estado": [{"resultado": r.value, "total": c} for r, c in resets_estado],
        "reincidentes": [{"email": e, "total": c} for e, c in reincidentes],
    }

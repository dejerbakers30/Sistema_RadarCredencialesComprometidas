# resets.py
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import client_meta, require_permission
from app.db.models.reset import Reset, ResetMetodo
from app.db.models.user import Usuario
from app.db.session import get_db
from app.schemas.reset import ResetManualRequest, ResetRead
from app.services.containment import contain_leak
from app.services.idp_client import build_idp
from fastapi import Request

router = APIRouter(prefix="/resets", tags=["resets"])


@router.get("", response_model=list[ResetRead])
def list_resets(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(require_permission("resets", "read"))],
    limit: int = 100,
):
    return db.execute(select(Reset).order_by(Reset.timestamp.desc()).limit(limit)).scalars().all()


@router.post("/manual", response_model=ResetRead)
async def manual_reset(
    payload: ResetManualRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[Usuario, Depends(require_permission("resets", "execute"))],
):
    idp = build_idp()
    try:
        reset = await contain_leak(
            db, idp, payload.leak_hit_id, metodo=ResetMetodo.manual, ejecutor_id=user.id
        )
    except ValueError as exc:
        raise HTTPException(404, str(exc))
    return reset

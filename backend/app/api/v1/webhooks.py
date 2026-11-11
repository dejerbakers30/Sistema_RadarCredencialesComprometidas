"""Recepción de callbacks firmados desde el IdP (p.ej. confirmación de reset)."""
import hashlib
import hmac
import logging

from fastapi import APIRouter, Header, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import Annotated

from app.core.config import settings
from app.db.session import get_db
from app.services.audit import write_audit

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def _verify_signature(body: bytes, signature: str) -> bool:
    if not settings.IDP_WEBHOOK_HMAC_SECRET:
        return False
    expected = hmac.new(
        settings.IDP_WEBHOOK_HMAC_SECRET.get_secret_value().encode(), body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/idp/callback")
async def idp_callback(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    x_radar_signature: str = Header(...),
):
    body = await request.body()
    if not _verify_signature(body, x_radar_signature):
        raise HTTPException(401, "Firma inválida")
    payload = await request.json()
    write_audit(
        db, modulo="webhooks", accion="idp_callback", resultado="ok",
        detalle={"action": payload.get("action"), "email": payload.get("email")},
    )
    logger.info("Callback IdP recibido: %s", payload.get("action"))
    return {"received": True}

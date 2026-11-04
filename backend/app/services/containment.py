"""Ejecuta reset + invalidación de sesiones con registro en resets y auditoría."""
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.leak import LeakEstado, LeakHit
from app.db.models.reset import Reset, ResetMetodo, ResetResultado
from app.services.audit import write_audit
from app.services.idp_client import BaseIdP, IdPResult

logger = logging.getLogger(__name__)


def _next_retry(intentos: int) -> datetime | None:
    schedule = settings.RETRY_BACKOFF_SCHEDULE_MIN
    if intentos - 1 >= len(schedule):
        return None
    return datetime.now(timezone.utc) + timedelta(minutes=schedule[intentos - 1])


async def contain_leak(
    db: Session,
    idp: BaseIdP,
    leak_hit_id: UUID,
    metodo: ResetMetodo = ResetMetodo.automatico,
    ejecutor_id: UUID | None = None,
) -> Reset:
    hit = db.execute(select(LeakHit).where(LeakHit.id == leak_hit_id)).scalar_one_or_none()
    if not hit:
        raise ValueError(f"LeakHit {leak_hit_id} no existe")

    # Desduplicación de contención: si ya hay reset exitoso, no repetir
    existente = db.execute(
        select(Reset).where(
            Reset.leak_hit_id == leak_hit_id,
            Reset.resultado == ResetResultado.exitoso,
        )
    ).scalar_one_or_none()
    if existente:
        logger.info("Leak %s ya contenido previamente", leak_hit_id)
        return existente

    reset = Reset(
        leak_hit_id=leak_hit_id,
        usuario_ejecutor=ejecutor_id,
        timestamp=datetime.now(timezone.utc),
        metodo=metodo,
        resultado=ResetResultado.pendiente,
        intentos=1,
    )
    db.add(reset)
    db.flush()

    email = hit.email_corporativo
    try:
        pwd_res = await idp.reset_password(email)
    except Exception as exc:
        logger.exception("Fallo IdP al restablecer contraseña para leak %s", leak_hit_id)
        pwd_res = IdPResult(False, error=str(exc))
    try:
        sess_res = await idp.revoke_sessions(email)
    except Exception as exc:
        logger.exception("Fallo IdP al revocar sesiones para leak %s", leak_hit_id)
        sess_res = IdPResult(False, error=str(exc))

    ok = pwd_res.ok and sess_res.ok
    reset.idp_respuesta = {
        "reset_password": {"ok": pwd_res.ok, "detail": pwd_res.detail, "error": pwd_res.error},
        "revoke_sessions": {"ok": sess_res.ok, "detail": sess_res.detail, "error": sess_res.error},
    }

    if ok:
        reset.resultado = ResetResultado.exitoso
        hit.estado = LeakEstado.contenido
        hit.fecha_contencion = datetime.now(timezone.utc)
    else:
        reset.resultado = ResetResultado.reintento
        reset.proximo_intento = _next_retry(reset.intentos)
        reset.error_detalle = f"pwd={pwd_res.error} sess={sess_res.error}"
        if reset.proximo_intento is None:
            reset.resultado = ResetResultado.fallido

    write_audit(
        db,
        modulo="resets",
        accion="auto_contain" if metodo == ResetMetodo.automatico else "manual_contain",
        entidad="leak_hits",
        entidad_id=str(leak_hit_id),
        resultado="ok" if ok else "error",
        usuario_id=ejecutor_id,
        usuario_email=None,
        detalle={"reset_id": str(reset.id), "resultado": reset.resultado.value},
    )
    db.flush()
    db.commit()
    logger.info("Contención leak=%s reset=%s resultado=%s", leak_hit_id, reset.id, reset.resultado.value)
    return reset

"""Procesa resets en estado reintento con backoff exponencial."""
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.leak import LeakEstado, LeakHit
from app.db.models.reset import Reset, ResetResultado
from app.services.audit import write_audit
from app.services.idp_client import BaseIdP

logger = logging.getLogger(__name__)


async def process_retries(db: Session, idp: BaseIdP) -> dict[str, int]:
    now = datetime.now(timezone.utc)
    pendientes = db.execute(
        select(Reset).where(
            Reset.resultado == ResetResultado.reintento,
            Reset.proximo_intento <= now,
        )
    ).scalars().all()

    stats = {"procesados": 0, "exitosos": 0, "fallidos": 0, "reprogramados": 0, "agotados": 0}

    for r in pendientes:
        stats["procesados"] += 1
        hit = db.get(LeakHit, r.leak_hit_id)
        if not hit:
            continue
        pwd_res = await idp.reset_password(hit.email_corporativo)
        sess_res = await idp.revoke_sessions(hit.email_corporativo)
        r.intentos += 1
        r.idp_respuesta = {
            "reset_password": {"ok": pwd_res.ok, "error": pwd_res.error},
            "revoke_sessions": {"ok": sess_res.ok, "error": sess_res.error},
        }
        if pwd_res.ok and sess_res.ok:
            r.resultado = ResetResultado.exitoso
            hit.estado = LeakEstado.contenido
            hit.fecha_contencion = datetime.now(timezone.utc)
            stats["exitosos"] += 1
        elif r.intentos >= settings.RETRY_MAX_ATTEMPTS:
            r.resultado = ResetResultado.fallido
            stats["agotados"] += 1
            write_audit(
                db, modulo="resets", accion="retry_exhausted",
                entidad="resets", entidad_id=str(r.id), resultado="error",
                detalle={"intentos": r.intentos},
            )
        else:
            from app.services.containment import _next_retry
            r.proximo_intento = _next_retry(r.intentos)
            stats["reprogramados"] += 1
        db.flush()

    logger.info("Reintentos: %s", stats)
    return stats

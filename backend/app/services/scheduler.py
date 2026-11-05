"""Jobs internos: reintentos, verificación de cadena, limpieza de caché."""
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.core.config import settings
from app.db.models.source import DominioMonitoreado
from app.db.session import session_scope
from app.services.audit import verify_chain
from app.services.containment import contain_leak
from app.services.correlation import collect_and_correlate
from app.services.hibp_client import HIBPClient
from app.services.idp_client import build_idp
from app.services.notifications import notify_admin_failure
from app.services.retry_queue import process_retries

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone="UTC")


async def job_collect() -> None:
    hibp = HIBPClient()
    with session_scope() as db:
        dominios = db.execute(
            select(DominioMonitoreado).where(DominioMonitoreado.activo.is_(True))
        ).scalars().all()
        for d in dominios:
            try:
                hits = await collect_and_correlate(db, hibp, d.dominio)
                idp = build_idp()
                for h in hits:
                    await contain_leak(db, idp, h.id)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Fallo recolección dominio %s", d.dominio)
                await notify_admin_failure(db, f"Fallo recolección {d.dominio}: {exc}")


async def job_retries() -> None:
    idp = build_idp()
    with session_scope() as db:
        await process_retries(db, idp)


async def job_verify_chain() -> None:
    with session_scope() as db:
        result = verify_chain(db)
        if not result["ok"]:
            await notify_admin_failure(db, f"Cadena de auditoría rota en IDs: {result['broken']}")
        logger.info("Verificación cadena: %s", result)


def start_scheduler() -> None:
    if settings.BACKEND_SCHEDULER_COLLECT_ENABLED:
        scheduler.add_job(job_collect, "cron", hour=3, minute=0, id="collect", replace_existing=True)
    scheduler.add_job(job_retries, "interval", minutes=15, id="retries", replace_existing=True)
    scheduler.add_job(
        job_verify_chain, "interval",
        hours=settings.AUDIT_VERIFY_INTERVAL_HOURS, id="verify_chain", replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler iniciado con %d jobs", len(scheduler.get_jobs()))


def stop_scheduler() -> None:
    scheduler.shutdown(wait=False)

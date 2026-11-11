"""Cruza emails filtrados contra directorio corporativo activo."""
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.leak import LeakEstado, LeakHit, LeakSeveridad
from app.db.models.source import Fuente
from app.db.models.user import Usuario
from app.services.dedup import canonical_hash
from app.services.hibp_client import HIBPClient

logger = logging.getLogger(__name__)


# Mapeo heurístico de severidad por tipo de dato expuesto
SEVERITY_MAP = {
    "Passwords": LeakSeveridad.critica,
    "Password": LeakSeveridad.critica,
    "Credit cards": LeakSeveridad.critica,
    "Bank account numbers": LeakSeveridad.alta,
    "Auth tokens": LeakSeveridad.alta,
    "Email addresses": LeakSeveridad.media,
    "Usernames": LeakSeveridad.media,
    "Phone numbers": LeakSeveridad.baja,
}


def infer_severity(breach_meta: dict) -> LeakSeveridad:
    data_classes = breach_meta.get("DataClasses", []) or []
    severities = [SEVERITY_MAP.get(dc, LeakSeveridad.baja) for dc in data_classes]
    if not severities:
        return LeakSeveridad.media
    order = [LeakSeveridad.baja, LeakSeveridad.media, LeakSeveridad.alta, LeakSeveridad.critica]
    return max(severities, key=order.index)


async def collect_and_correlate(db: Session, hibp: HIBPClient, dominio: str) -> list[LeakHit]:
    """Recolecta HIBP, correlaciona con directorio y persiste solo matches."""
    # 1. Directorio activo
    users = db.execute(
        select(Usuario.email, Usuario.id).where(Usuario.activo.is_(True))
    ).all()
    email_to_user = {email.lower(): uid for email, uid in users}

    # 2. HIBP
    breaches_by_email = await hibp.breached_domain(dominio)
    catalog = {b["Name"]: b for b in await hibp.all_breaches()}

    # 3. Fuente HIBP
    fuente = db.execute(select(Fuente).where(Fuente.nombre == "hibp")).scalar_one_or_none()
    if not fuente:
        fuente = Fuente(nombre="hibp", tipo="api", endpoint=hibp.base_url, activa=True)
        db.add(fuente)
        db.flush()

    hits: list[LeakHit] = []
    now = datetime.now(timezone.utc)

    for email, breach_names in breaches_by_email.items():
        email_l = email.lower()
        user_id = email_to_user.get(email_l)
        if not user_id:
            continue  # no es usuario corporativo activo → no se persiste
        for bname in breach_names:
            meta = catalog.get(bname, {})
            fecha_breach = None
            if meta.get("BreachDate"):
                try:
                    fecha_breach = datetime.fromisoformat(meta["BreachDate"]).date()
                except ValueError:
                    pass
            h = canonical_hash(email_l, bname, fecha_breach)
            exists = db.execute(
                select(LeakHit.id).where(LeakHit.hash_canonico == h)
            ).scalar_one_or_none()
            if exists:
                continue  # desduplicación
            hit = LeakHit(
                email_corporativo=email_l,
                usuario_id=user_id,
                breach_origen=bname,
                breach_dominio=meta.get("Domain"),
                fecha_breach=fecha_breach,
                fecha_deteccion=now,
                severidad=infer_severity(meta),
                fuente_id=fuente.id,
                fuente_detalle=f"HIBP/{bname}",
                datos_expuestos=meta.get("DataClasses"),
                estado=LeakEstado.nuevo,
                hash_canonico=h,
            )
            db.add(hit)
            hits.append(hit)

    db.flush()
    logger.info("Correlación dominio=%s nuevos_hits=%d", dominio, len(hits))
    return hits

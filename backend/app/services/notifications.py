"""Notificaciones por email (SMTP) y chat (Teams/Slack)."""
import logging
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.leak import LeakHit
from app.db.models.notification import Notificacion

logger = logging.getLogger(__name__)


TEMPLATE_USER = """\
Hola {nombre},

Nuestro sistema de monitoreo ha detectado que tu correo corporativo ({email})
aparece en la filtración de datos "{breach}" ({fecha}).

Acción tomada automáticamente:
- Se ha forzado el restablecimiento de tu contraseña.
- Se han invalidado tus sesiones activas.

Debes establecer una nueva contraseña en tu próximo inicio de sesión y
verificar que no existan accesos no autorizados. Si detectas actividad
sospechosa, contacta con seguridad@example.com.

Este aviso es informativo y no implica que tu cuenta haya sido comprometida.
"""


def _send_email(to: str, subject: str, body: str) -> tuple[bool, str | None]:
    if not settings.SMTP_HOST:
        return False, "SMTP no configurado"
    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()
            if settings.SMTP_USER:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD.get_secret_value())
            smtp.send_message(msg)
        return True, None
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


async def _send_chat(text: str) -> tuple[bool, str | None]:
    for url in (settings.TEAMS_WEBHOOK_URL, settings.SLACK_WEBHOOK_URL):
        if not url:
            continue
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json={"text": text})
            if resp.status_code < 300:
                return True, None
            return False, f"HTTP {resp.status_code}"
        except httpx.HTTPError as exc:
            return False, str(exc)
    return False, "Sin webhook configurado"


def notify_user(db: Session, hit: LeakHit, nombre: str) -> Notificacion:
    body = TEMPLATE_USER.format(
        nombre=nombre,
        email=hit.email_corporativo,
        breach=hit.breach_origen,
        fecha=hit.fecha_breach or "fecha desconocida",
    )
    ok, err = _send_email(hit.email_corporativo, "Aviso de seguridad: credencial filtrada", body)
    n = Notificacion(
        leak_hit_id=hit.id,
        destinatario=hit.email_corporativo,
        canal="email",
        plantilla="user_breach_notice",
        enviado_en=datetime.now(timezone.utc) if ok else None,
        estado="enviado" if ok else "fallido",
        error_detalle=err,
    )
    db.add(n)
    db.flush()
    return n


async def notify_admin_failure(db: Session, mensaje: str) -> None:
    await _send_chat(f":rotating_light: Radar Creds — {mensaje}")

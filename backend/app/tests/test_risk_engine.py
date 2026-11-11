import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timezone
from app.db.models.leak import LeakEstado, LeakHit, LeakSeveridad
from app.db.models.source import Fuente
from app.services.containment import contain_leak
from app.services.idp_client import IdPResult
from app.services.risk_engine import risk_engine


def test_risk_engine_classification():
    # Contraseñas críticas
    assert risk_engine.evaluate("123456") == "Crítico"
    assert risk_engine.evaluate("password") == "Crítico"
    assert risk_engine.evaluate("qwerty") == "Crítico"
    assert risk_engine.evaluate("admin") == "Crítico"
    assert risk_engine.evaluate("") == "Crítico"
    assert risk_engine.evaluate(None) == "Crítico"

    # Contraseñas robustas
    strong_pwd = "k9#mP$2vL!9xQ8#zM1"
    assert risk_engine.evaluate(strong_pwd) == "Bajo"


@pytest.mark.asyncio
async def test_containment_with_low_risk(db):
    f = Fuente(nombre="test_low", tipo="api", activa=True)
    db.add(f)
    db.flush()

    hit = LeakHit(
        email_corporativo="safe.user@example.com",
        breach_origen="TestBreach",
        fecha_deteccion=datetime.now(timezone.utc),
        severidad=LeakSeveridad.baja,
        fuente_id=f.id,
        estado=LeakEstado.nuevo,
        hash_canonico="h" * 63 + "1",
    )
    db.add(hit)
    db.flush()

    idp = AsyncMock()
    # Password de bajo riesgo
    reset = await contain_leak(db, idp, hit.id, password_candidata="k9#mP$2vL!9xQ8#zM1")

    # Debe omitir llamada a IdP y no bloquear
    idp.reset_password.assert_not_called()
    idp.revoke_sessions.assert_not_called()
    assert hit.estado == LeakEstado.falso_positivo
    assert hit.score_riesgo == "Bajo"
    assert reset.resultado.value == "exitoso"


@pytest.mark.asyncio
async def test_containment_with_critical_risk(db):
    f = Fuente(nombre="test_crit", tipo="api", activa=True)
    db.add(f)
    db.flush()

    hit = LeakHit(
        email_corporativo="victim.user@example.com",
        breach_origen="TestBreach",
        fecha_deteccion=datetime.now(timezone.utc),
        severidad=LeakSeveridad.alta,
        fuente_id=f.id,
        estado=LeakEstado.nuevo,
        hash_canonico="h" * 63 + "2",
    )
    db.add(hit)
    db.flush()

    idp = AsyncMock()
    idp.reset_password.return_value = IdPResult(True)
    idp.revoke_sessions.return_value = IdPResult(True)

    # Password crítica (típica de RockYou)
    reset = await contain_leak(db, idp, hit.id, password_candidata="123456")

    idp.reset_password.assert_called_once_with("victim.user@example.com")
    idp.revoke_sessions.assert_called_once_with("victim.user@example.com")
    assert hit.estado == LeakEstado.contenido
    assert hit.score_riesgo == "Crítico"
    assert reset.resultado.value == "exitoso"


import pytest
from unittest.mock import AsyncMock
from app.db.models.leak import LeakEstado, LeakHit, LeakSeveridad
from app.db.models.source import Fuente
from app.services.containment import contain_leak
from app.services.idp_client import IdPResult


@pytest.mark.asyncio
async def test_containment_success(db):
    f = Fuente(nombre="test", tipo="api", activa=True)
    db.add(f); db.flush()
    hit = LeakHit(
        email_corporativo="a@b.com", breach_origen="X", fecha_deteccion=__import__("datetime").datetime.now(),
        severidad=LeakSeveridad.alta, fuente_id=f.id, estado=LeakEstado.nuevo,
        hash_canonico="h" * 64,
    )
    db.add(hit); db.flush()
    idp = AsyncMock()
    idp.reset_password.return_value = IdPResult(True)
    idp.revoke_sessions.return_value = IdPResult(True)
    reset = await contain_leak(db, idp, hit.id)
    assert reset.resultado.value == "exitoso"
    assert hit.estado == LeakEstado.contenido

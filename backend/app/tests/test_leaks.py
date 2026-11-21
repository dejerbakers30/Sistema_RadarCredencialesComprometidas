from datetime import UTC


def test_kpis_endpoint_requires_permission(client):
    r = client.get("/api/v1/leaks/kpis")
    assert r.status_code == 401  # sin token


def test_leaks_read_serializes_reserved_fixture_domains(client, db):
    from datetime import datetime
    from uuid import uuid4

    from sqlalchemy import select

    from app.api.deps import get_current_user
    from app.db.models.leak import LeakEstado, LeakHit, LeakSeveridad
    from app.db.models.source import Fuente
    from app.db.models.user import Role, Usuario
    from app.main import app
    source = Fuente(nombre="fixture-read-" + uuid4().hex[:8], tipo="api", activa=True)
    role = db.execute(select(Role).where(Role.nombre == "auditor")).scalar_one()
    user = Usuario(email=uuid4().hex + "@example.test", nombre="Fixture reader", rol_id=role.id)
    db.add_all([source, user]); db.flush()
    hit = LeakHit(email_corporativo="read-fixture@example.test", breach_origen="Fixture Read",
                  fecha_deteccion=datetime.now(UTC), severidad=LeakSeveridad.media,
                  fuente_id=source.id, estado=LeakEstado.nuevo, hash_canonico=uuid4().hex * 2)
    db.add(hit); db.commit()
    app.dependency_overrides[get_current_user] = lambda: user
    response = client.get("/api/v1/leaks?limit=100")
    assert response.status_code == 200
    assert any(row["email_corporativo"] == "read-fixture@example.test" for row in response.json())

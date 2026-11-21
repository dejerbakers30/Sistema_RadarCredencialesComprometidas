import json
import time
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.api.deps import get_current_user
from app.db.models.audit import AuditLog
from app.db.models.user import Role, Usuario
from app.main import app
from app.ml.storage import storage_root
from tests_ml.test_training import fixture_csv, provenance


@pytest.fixture
def ml_store(tmp_path, monkeypatch):
    monkeypatch.setenv("RADAR_ML_STORAGE", str(tmp_path / "ml"))


def login_as(db, role_name):
    role = db.execute(select(Role).where(Role.nombre == role_name)).scalar_one()
    user = Usuario(email=f"ml-{uuid4().hex}@example.test", nombre="ML test", rol_id=role.id)
    db.add(user)
    db.commit()
    app.dependency_overrides[get_current_user] = lambda: user
    return user


def test_training_requires_authentication(client, ml_store):
    assert client.get("/api/v1/training/overview").status_code == 401
    assert client.get("/api/v1/training/template").status_code == 401


def test_reader_cannot_modify_registry(client, db, ml_store):
    login_as(db, "auditor")
    assert client.get("/api/v1/training/overview").status_code == 200
    assert client.post("/api/v1/training/deactivate").status_code == 403
    assert client.post("/api/v1/training/runs", json={"dataset_id": str(uuid4())}).status_code == 403


def test_api_training_export_and_synthetic_activation_guard(client, db, ml_store):
    user = login_as(db, "admin")
    imported = client.post("/api/v1/training/datasets",
                           files={"file": ("fixture.csv", fixture_csv(), "text/csv")},
                           data={"provenance": provenance().model_dump_json()})
    assert imported.status_code == 201, imported.text
    dataset_id = imported.json()["id"]
    started = client.post("/api/v1/training/runs", json={"dataset_id": dataset_id,
                          "config": {"trials": 1, "folds": 2, "max_seconds": 120}})
    assert started.status_code == 202, started.text
    identifier = started.json()["id"]
    duplicate = client.post("/api/v1/training/runs", json={"dataset_id": dataset_id})
    assert duplicate.status_code == 409
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        response = client.get(f"/api/v1/training/runs/{identifier}")
        assert response.status_code == 200
        record = response.json()
        if record["status"] not in ("queued", "running"):
            break
        time.sleep(0.2)
    assert record["status"] == "completed", record
    exported = client.get(f"/api/v1/training/runs/{identifier}/export")
    assert exported.status_code == 200
    assert set(exported.json()["predictions"]["predictions"]) == {"M1", "M2", "M3"}
    assert "password" not in exported.json()["predictions"]
    from app.ml.datasets import load_dataset
    X, _, _, _ = load_dataset(dataset_id)
    predicted = client.post(f"/api/v1/training/runs/{identifier}/predict",
                            json={"features": X[0].tolist()})
    assert predicted.status_code == 200
    assert predicted.json()["preview"] is True
    assert predicted.json()["label"] in ("Bajo", "Medio", "Crítico")
    assert client.post(f"/api/v1/training/runs/{identifier}/predict",
                       json={"features": [1, 2]}).status_code == 422
    assert client.post(f"/api/v1/training/runs/{identifier}/predict",
                       json={"features": X[0].tolist(), "password": "not-accepted"}).status_code == 422
    activate = client.post(f"/api/v1/training/runs/{identifier}/activate")
    assert activate.status_code == 409
    assert not (storage_root() / "active.json").exists()
    audit = db.execute(select(AuditLog).where(AuditLog.modulo == "training",
                                            AuditLog.usuario_id == str(user.id))).scalars().all()
    assert {entry.accion for entry in audit} >= {"dataset_imported", "training_started"}
    assert all("password" not in json.dumps(entry.detalle or {}) for entry in audit)

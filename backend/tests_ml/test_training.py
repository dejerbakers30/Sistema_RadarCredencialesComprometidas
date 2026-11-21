"""Pruebas con datos sintéticos: no constituyen evidencia científica del caso."""
import csv
import io
import random
import string
import time
from uuid import uuid4

import numpy as np
import pytest

from app.ml import manager
from app.ml.datasets import import_dataset, load_dataset, partition
from app.ml.inference import load_verified, predict_features
from app.ml.schema import FEATURES, LABELS, Provenance, RunConfig
from app.ml.storage import now, read_json, record_path, storage_root, write_json
from app.ml.training import train_run
from app.services.risk_engine import RiskEngine, extract_features


def fixture_csv(size=360):
    """Genera valores artificiales en memoria y exporta solo características."""
    rng = random.Random(501)
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow([*FEATURES, "label", "group_id"])
    alphabet = string.ascii_letters + string.digits + "!#@$%"
    for i in range(size):
        category = i % 3
        length = rng.randint(*[(5, 7), (9, 12), (15, 23)][category])
        value = "".join(rng.choice(alphabet) for _ in range(length))
        writer.writerow([*extract_features(value), LABELS[2-category], f"family_{i}"])
    return stream.getvalue().encode()


def provenance():
    return Provenance(source="synthetic-fixture-v1", license="Test-only generated data",
                      label_method="Synthetic labels from length bands, for software verification only.",
                      kind="synthetic", authorized=True)


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("RADAR_ML_STORAGE", str(tmp_path / "ml"))


def make_run(config=None):
    dataset = import_dataset(fixture_csv(), provenance())
    identifier = str(uuid4())
    write_json(record_path("runs", identifier) / "record.json", {
        "id": identifier, "dataset_id": dataset["id"], "created_at": now(),
        "config": (config or RunConfig(trials=1, folds=2, max_seconds=120)).model_dump(),
        "status": "queued", "phase": "test", "progress": 0,
    })
    return identifier


def test_schema_rejects_plaintext_and_bad_values():
    content = fixture_csv()
    with pytest.raises(ValueError, match="Cabecera"):
        import_dataset(content.replace(b"length,", b"password,"), provenance())
    with pytest.raises(ValueError, match="numéricas|esquema"):
        import_dataset(content.replace(b"5,", b"nan,", 1), provenance())
    with pytest.raises(ValueError):
        import_dataset(content.replace(b"family_0", b"person@example.com"), provenance())
    with pytest.raises(ValueError):
        import_dataset(content[:50], provenance())


def test_group_split_and_cv_have_no_overlap_and_reproduce():
    record = import_dataset(fixture_csv(), provenance())
    X, y, groups, _ = load_dataset(record["id"])
    train, val, test, cv = partition(X, y, groups, 42, 3)
    again = partition(X, y, groups, 42, 3)
    for original, repeated in zip((train, val, test), again[:3]):
        np.testing.assert_array_equal(original, repeated)
        assert set(y[original]) == set(LABELS)
    assert not set(groups[train]) & set(groups[val])
    assert not set(groups[train]) & set(groups[test])
    assert not set(groups[val]) & set(groups[test])
    for a, b in cv:
        assert not set(groups[train[a]]) & set(groups[train[b]])
        assert not set(train[b]) & set(test)


def test_identical_vectors_cannot_cross_groups():
    content = fixture_csv().decode().splitlines()
    duplicate = content[1].rsplit(",", 1)[0] + ",duplicate_family"
    dataset = import_dataset(("\n".join([*content, duplicate]) + "\n").encode(), provenance())
    _X, _y, groups, _ = load_dataset(dataset["id"])
    assert groups[0] == groups[-1]
    assert dataset["duplicates"] > 0
    contradicted = duplicate.replace(",Crítico,", ",Bajo,")
    ambiguous = import_dataset(("\n".join([*content, contradicted]) + "\n").encode(), provenance())
    assert ambiguous["ambiguous_feature_vectors"] >= 1
    # Mismas características no implican la misma contraseña ni la misma etiqueta.
    _X, _y, joined_groups, _ = load_dataset(ambiguous["id"])
    assert joined_groups[0] == joined_groups[-1]


def test_complete_run_freezes_before_test_and_inference_is_identical():
    identifier = make_run()
    train_run(identifier)
    directory = record_path("runs", identifier)
    record = read_json(directory / "record.json")
    assert record["status"] == "completed", record
    assert record["frozen_at"] <= record["test_opened_at"]
    assert set(record["models"]) == {"M1", "M2", "M3"}
    assert record["selected_model"] == max(record["models"], key=lambda k: record["models"][k]["validation"]["macro_f1"])
    model, _ = load_verified(identifier)
    X, _, _, _ = load_dataset(record["dataset_id"])
    write_json(storage_root() / "active.json", {"run_id": identifier})
    assert predict_features(X[0]) == model.predict(X[:1])[0]
    for candidate in ("password", "12345", "abcdefghijklmNOP123!@#"):
        assert RiskEngine().evaluate(candidate) == model.predict([extract_features(candidate)])[0]
    pred = read_json(directory / "predictions.json")
    idx = pred["row_index"]
    assert model.predict(X[idx]).tolist() == pred["predictions"][record["selected_model"]]
    (directory / f'{record["selected_model"]}.joblib').write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="integridad"):
        load_verified(identifier)
    # La corrupción no interrumpe el fallback de inferencia.
    assert RiskEngine().evaluate("abcdefghijklmNOP123!@#") in LABELS


def test_dataset_integrity_and_path_traversal():
    record = import_dataset(fixture_csv(), provenance())
    (record_path("datasets", record["id"]) / "features.npz").write_bytes(b"changed")
    with pytest.raises(ValueError, match="integridad"):
        load_dataset(record["id"])
    with pytest.raises(ValueError):
        record_path("runs", "../../etc/passwd")


def test_cancelled_run_never_replaces_active_pointer():
    write_json(storage_root() / "active.json", {"run_id": str(uuid4())})
    before = (storage_root() / "active.json").read_bytes()
    identifier = make_run()
    manager.cancel_run(identifier)
    train_run(identifier)
    assert read_json(record_path("runs", identifier) / "record.json")["status"] == "cancelled"
    assert (storage_root() / "active.json").read_bytes() == before


def test_worker_is_exclusive_and_survives_manager_return():
    dataset = import_dataset(fixture_csv(), provenance())
    cfg = RunConfig(trials=1, folds=2, max_seconds=120)
    record = manager.start_run(dataset["id"], cfg, "test")
    with pytest.raises(ValueError, match="activo"):
        manager.start_run(dataset["id"], cfg, "test")
    manager.cancel_run(record["id"])
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        current = read_json(record_path("runs", record["id"]) / "record.json")
        if current["status"] not in ("queued", "running"):
            break
        time.sleep(0.1)
    assert current["status"] == "cancelled"


def test_inference_does_not_train_at_import(monkeypatch):
    from sklearn.linear_model import LogisticRegression
    monkeypatch.setattr(LogisticRegression, "fit", lambda *args, **kwargs: pytest.fail("No debe entrenar"))
    engine = RiskEngine()
    assert engine.evaluate("123456") == "Crítico"
    assert engine.evaluate("k9#mP$2vL!9xQ8#zM1") == "Bajo"

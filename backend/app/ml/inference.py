"""Carga exclusivamente artefactos locales generados y registrados por el laboratorio."""
import threading

import joblib
import numpy as np
import sklearn

from app.ml.schema import FEATURES, LABELS, SCHEMA_VERSION
from app.ml.storage import digest, read_json, record_path, storage_root

_cache = {}
_lock = threading.Lock()


def verified_artifact(identifier):
    directory = record_path("runs", identifier)
    record = read_json(directory / "record.json")
    if record["status"] != "completed" or record.get("schema") != SCHEMA_VERSION:
        raise ValueError("Solo se pueden activar ejecuciones completas con el esquema vigente.")
    if record["environment"]["sklearn"] != sklearn.__version__:
        raise ValueError("La versión de scikit-learn difiere de la utilizada al entrenar.")
    name = record["selected_model"]
    if name not in ("M1", "M2", "M3"):
        raise ValueError("Modelo no reconocido.")
    path = directory / f"{name}.joblib"
    expected = record["models"][name]["artifact_sha256"]
    if digest(path) != expected:
        raise ValueError("El artefacto no supera la verificación de integridad.")
    return record, path, expected


def load_verified(identifier):
    record, path, expected = verified_artifact(identifier)
    key = (str(path), expected)
    with _lock:
        if key not in _cache:
            # Nunca se aceptan joblib/pickle subidos por el usuario.
            model = joblib.load(path)
            if model.n_features_in_ != len(FEATURES) or set(model.classes_) != set(LABELS):
                raise ValueError("El artefacto no tiene las variables o clases requeridas.")
            _cache.clear()
            _cache[key] = model
        return _cache[key], record


def active_status():
    pointer = storage_root() / "active.json"
    if not pointer.exists():
        return {"mode": "heuristic_fallback", "run_id": None,
                "detail": "Sin modelo registrado activo; reglas conservadoras de debilidad."}
    try:
        active = read_json(pointer)
        record, _, _ = verified_artifact(active["run_id"])
        return {**active, "mode": "registered", "selected_model": record["selected_model"],
                "kind": record["dataset"]["provenance"]["kind"]}
    except Exception:  # noqa: BLE001 - el estado público no revela rutas ni datos del artefacto
        return {"mode": "invalid_artifact", "run_id": None,
                "detail": "Artefacto no válido; se aplican reglas conservadoras."}


def predict_features(features):
    pointer = storage_root() / "active.json"
    if not pointer.exists():
        return None
    model, _ = load_verified(read_json(pointer)["run_id"])
    return str(model.predict(np.asarray([features], dtype=float))[0])

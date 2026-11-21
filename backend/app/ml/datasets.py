"""Importa características; nunca conserva contraseñas ni identificadores originales."""
import csv
import hashlib
import hmac
import io
import re
import secrets
from collections import Counter
from itertools import islice
from uuid import uuid4

import numpy as np
from sklearn.model_selection import GroupShuffleSplit, StratifiedGroupKFold

from app.ml.schema import FEATURES, LABELS, SCHEMA_VERSION, Provenance
from app.ml.storage import digest, now, read_json, record_path, write_json

MAX_BYTES = 3_000_000
MAX_ROWS = 20_000


def validate_feature_vector(values):
    length, entropy, digits, upper, symbols, pattern, only, count = values
    if (not np.isfinite(values).all() or length < 1 or length > 256 or length != int(length)
            or entropy < 0 or entropy > np.log2(length) + 1e-6
            or not all(0 <= r <= 1 for r in [digits, upper, symbols])
            or digits + upper + symbols > 1.000001
            or pattern not in (0, 1) or only not in (0, 1)
            or count != int(count) or not 0 <= count <= length
            or not np.isclose(symbols * length, count, atol=1e-5)):
        raise ValueError("Hay características fuera del esquema password-features-v1.")
    return values


def import_dataset(content: bytes, provenance: Provenance) -> dict:
    if len(content) > MAX_BYTES:
        raise ValueError("El CSV supera el límite de 3 MB.")
    try:
        reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
        expected = [*FEATURES, "label", "group_id"]
        if reader.fieldnames != expected:
            raise ValueError("Cabecera inválida. Descarga la plantilla con las columnas exactas.")
        rows = list(islice(reader, MAX_ROWS + 1))
    except UnicodeError as exc:
        raise ValueError("El CSV debe utilizar UTF-8.") from exc
    if not 90 <= len(rows) <= MAX_ROWS:
        raise ValueError("Se requieren entre 90 y 20000 observaciones.")
    X, y, raw_groups = [], [], []
    for row in rows:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("El CSV contiene filas incompletas o columnas adicionales.")
        if row["label"] not in LABELS or not re.fullmatch(r"[a-zA-Z0-9_-]{1,100}", row["group_id"]):
            raise ValueError("Clases inválidas o group_id no opaco; usa identificadores sin datos personales.")
        try:
            values = np.array([float(row[name]) for name in FEATURES])
        except ValueError as exc:
            raise ValueError("Las características deben ser numéricas.") from exc
        values = validate_feature_vector(values)
        X.append(values)
        y.append(row["label"])
        raw_groups.append(row["group_id"])
    X, y = np.array(X), np.array(y)
    counts = Counter(y.tolist())
    if set(counts) != set(LABELS) or min(counts.values()) < 20:
        raise ValueError("Cada una de las tres clases necesita al menos 20 observaciones.")

    # Une grupos relacionados por vectores idénticos; no permite copias entre particiones.
    parent = {group: group for group in raw_groups}

    def find(group):
        while parent[group] != group:
            parent[group] = parent[parent[group]]
            group = parent[group]
        return group

    seen = {}
    feature_labels = {}
    for values, label, group in zip(X, y, raw_groups):
        key = tuple(values)
        feature_labels.setdefault(key, set()).add(str(label))
        if key in seen:
            previous_group, _previous_label = seen[key]
            parent[find(group)] = find(previous_group)
        else:
            seen[key] = (group, label)
    salt = secrets.token_bytes(32)
    groups = np.array([hmac.new(salt, find(g).encode(), "sha256").hexdigest() for g in raw_groups])
    for label in LABELS:
        if len(set(groups[y == label])) < 10:
            raise ValueError("Cada clase requiere al menos diez grupos independientes tras deduplicación.")
    identifier = str(uuid4())
    directory = record_path("datasets", identifier)
    directory.mkdir(parents=True, mode=0o700)
    np.savez_compressed(directory / "features.npz", X=X, y=y, groups=groups)
    summary = {
        "id": identifier, "created_at": now(), "schema": SCHEMA_VERSION,
        "source_sha256": hashlib.sha256(content).hexdigest(),
        "features_sha256": digest(directory / "features.npz"),
        "provenance": provenance.model_dump(), "rows": len(y), "groups": len(set(groups)),
        "duplicates": len(y) - len(seen),
        "ambiguous_feature_vectors": sum(len(labels) > 1 for labels in feature_labels.values()),
        "classes": counts,
        "features": [{"name": name, "min": float(X[:, i].min()),
                      "max": float(X[:, i].max()), "mean": float(X[:, i].mean()),
                      "std": float(X[:, i].std())} for i, name in enumerate(FEATURES)],
        "limitation": "Estudio transversal de debilidad. No mide exposición ni probabilidad de ataque.",
    }
    write_json(directory / "record.json", summary)
    return summary


def load_dataset(identifier):
    directory = record_path("datasets", identifier)
    record = read_json(directory / "record.json")
    if digest(directory / "features.npz") != record["features_sha256"]:
        raise ValueError("La integridad del dataset no coincide con su registro.")
    with np.load(directory / "features.npz", allow_pickle=False) as data:
        return data["X"], data["y"], data["groups"], record


def partition(X, y, groups, seed, folds):
    labels = set(LABELS)
    best = None
    # Busca tamaños cercanos a 70/15/15 conservando grupos enteros y las tres clases.
    for attempt in range(120):
        train, rest = next(GroupShuffleSplit(n_splits=1, test_size=0.30,
                                            random_state=seed + attempt).split(X, y, groups))
        left, right = next(GroupShuffleSplit(n_splits=1, test_size=0.50,
                                            random_state=seed + attempt).split(X[rest], y[rest], groups[rest]))
        val, test = rest[left], rest[right]
        if any(set(y[index]) != labels for index in (train, val, test)):
            continue
        cv = list(StratifiedGroupKFold(n_splits=folds, shuffle=True, random_state=seed)
                  .split(X[train], y[train], groups[train]))
        if any(set(y[train[a]]) != labels or set(y[train[b]]) != labels for a, b in cv):
            continue
        error = sum(abs(len(index) / len(y) - ratio)
                    for index, ratio in zip((train, val, test), (0.70, 0.15, 0.15)))
        error += sum(abs(np.mean(y[index] == label) - np.mean(y == label))
                     for index in (train, val, test) for label in LABELS)
        if best is None or error < best[0]:
            best = error, train, val, test, cv
    if best is None:
        raise ValueError("No hay grupos suficientes para una partición y folds con las tres clases.")
    return best[1:]

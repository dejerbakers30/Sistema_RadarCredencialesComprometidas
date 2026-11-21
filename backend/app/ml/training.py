"""Entrenamiento reproducible; prueba reservada hasta congelar la selección."""
import itertools
import platform
import subprocess
import time
import warnings
from pathlib import Path

import joblib
import numpy as np
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
    roc_auc_score,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, label_binarize
from threadpoolctl import threadpool_limits

from app.ml.datasets import load_dataset, partition
from app.ml.schema import FEATURES, LABELS, MODEL_CARDS, SCHEMA_VERSION, RunConfig
from app.ml.storage import digest, list_records, now, read_json, record_path, write_json


class Cancelled(Exception):
    pass


def build_model(model_id, params, seed):
    if model_id == "M1":
        return make_pipeline(StandardScaler(), LogisticRegression(
            **params, solver="lbfgs", class_weight="balanced", random_state=seed))
    if model_id == "M2":
        return RandomForestClassifier(**params, max_features="sqrt", class_weight="balanced",
                                      random_state=seed, n_jobs=1)
    return HistGradientBoostingClassifier(**params, early_stopping=False,
                                          class_weight="balanced", random_state=seed)


def candidates(model_id, config):
    initial = getattr(config, model_id.lower()).model_dump()
    search = next(card["search"] for card in MODEL_CARDS if card["id"] == model_id)
    grid = [dict(zip(search, values)) for values in itertools.product(*search.values())]
    rng = np.random.default_rng(config.seed)
    rng.shuffle(grid)
    result = [initial]
    for values in grid:
        proposal = {**initial, **values}
        if proposal not in result:
            result.append(proposal)
        if len(result) == config.trials:
            break
    return result[:config.trials]


def metrics(model, X, y):
    start = time.perf_counter()
    prediction = model.predict(X)
    probability = model.predict_proba(X)
    latency = (time.perf_counter() - start) * 1000 / len(y)
    order = [list(model.classes_).index(label) for label in LABELS]
    probability = probability[:, order]
    binary = label_binarize(y, classes=list(LABELS))
    # log_loss expects probabilities ordered lexicographically, not display order.
    lex_order = sorted(range(len(LABELS)), key=lambda i: LABELS[i])
    return {
        "macro_f1": float(f1_score(y, prediction, average="macro", labels=LABELS, zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y, prediction)),
        "confusion_matrix": confusion_matrix(y, prediction, labels=LABELS).tolist(),
        "labels": list(LABELS),
        "per_class": classification_report(y, prediction, labels=LABELS, output_dict=True,
                                            zero_division=0),
        "pr_auc_macro_ovr": float(average_precision_score(binary, probability, average="macro")),
        "roc_auc_macro_ovr": float(roc_auc_score(binary, probability, average="macro")),
        "brier_multiclass": float(np.mean(np.sum((probability - binary)**2, axis=1))),
        "log_loss": float(log_loss(y, probability[:, lex_order], labels=sorted(LABELS))),
        "latency_ms_per_row_batch": latency,
    }, prediction


def bootstrap(y, prediction, groups, seed):
    unique = np.unique(groups)
    by_group = {group: np.flatnonzero(groups == group) for group in unique}
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(200):
        idx = np.concatenate([by_group[g] for g in rng.choice(unique, len(unique), replace=True)])
        values.append(f1_score(y[idx], prediction[idx], labels=LABELS,
                               average="macro", zero_division=0))
    return {"method": "percentile group bootstrap", "resamples": 200,
            "macro_f1_95_ci": np.quantile(values, [0.025, 0.975]).tolist()}


def train_run(identifier):
    directory = record_path("runs", identifier)
    record = read_json(directory / "record.json")
    config = RunConfig.model_validate(record["config"])
    start = time.monotonic()

    def checkpoint(phase=None, progress=None):
        if (directory / "cancel").exists():
            raise Cancelled()
        if time.monotonic() - start > config.max_seconds:
            raise TimeoutError()
        if phase:
            record.update(status="running", phase=phase, updated_at=now())
        if progress is not None:
            record["progress"] = progress
        write_json(directory / "record.json", record)

    try:
        checkpoint("Preparando particiones independientes", 2)
        X, y, groups, dataset = load_dataset(record["dataset_id"])
        previous = sum(r.get("test_opened_at") is not None
                       and r.get("dataset", {}).get("source_sha256") == dataset["source_sha256"]
                       for r in list_records("runs") if r["id"] != identifier)
        record["previous_test_openings_same_source"] = previous
        train, val, test, cv = partition(X, y, groups, config.seed, config.folds)
        split = {name: {"rows": len(idx), "groups": len(set(groups[idx])),
                        "ratio": len(idx) / len(y),
                        "classes": {label: int(np.sum(y[idx] == label)) for label in LABELS}}
                 for name, idx in zip(("train", "validation", "test"), (train, val, test))}
        np.savez_compressed(directory / "partition.npz", train=train, validation=val, test=test,
                            **{f"fold_{i}_{part}": train[idx] for i, pair in enumerate(cv)
                               for part, idx in zip(("train", "validation"), pair)})
        try:
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"],
                                             cwd=Path(__file__).parents[3], stderr=subprocess.DEVNULL,
                                             text=True).strip()
        except (OSError, subprocess.CalledProcessError):
            commit = "unavailable"
        record.update(partition=split, dataset=dataset, environment={
            "python": platform.python_version(), "sklearn": sklearn.__version__,
            "numpy": np.__version__, "joblib": joblib.__version__, "platform": platform.platform(),
            "cpu": platform.processor() or platform.machine(), "cpu_threads_used": 1,
            "commit": commit, "partition_sha256": digest(directory / "partition.npz"),
            "code_sha256": {str(path.relative_to(Path(__file__).parents[2])): digest(path)
                            for path in [*Path(__file__).parent.glob("*.py"),
                                         Path(__file__).parents[1] / "services" / "risk_engine.py"]},
        }, models={}, selection_metric="validation.macro_f1", test_opened_at=None)
        fitted = {}
        total = 3 * config.trials * config.folds
        done = 0
        with threadpool_limits(limits=1):
            for model_id in ("M1", "M2", "M3"):
                history = []
                best = None
                training_start = time.perf_counter()
                for trial, params in enumerate(candidates(model_id, config)):
                    scores = []
                    try:
                        for fold, (a, b) in enumerate(cv):
                            checkpoint(f"{model_id} · ensayo {trial+1}/{config.trials} · fold {fold+1}",
                                       5 + int(70 * done / total))
                            model = build_model(model_id, params, config.seed)
                            with warnings.catch_warnings():
                                warnings.simplefilter("error", ConvergenceWarning)
                                model.fit(X[train[a]], y[train[a]])
                            prediction = model.predict(X[train[b]])
                            scores.append(float(f1_score(y[train[b]], prediction, labels=LABELS,
                                                         average="macro", zero_division=0)))
                            done += 1
                        value = float(np.mean(scores))
                        history.append({"trial": trial, "params": params, "fold_scores": scores,
                                        "macro_f1": value, "status": "completed"})
                        if best is None or value > best[0]:
                            best = value, params
                    except ConvergenceWarning:
                        history.append({"trial": trial, "params": params,
                                        "status": "non_converged", "fold_scores": scores})
                if best is None:
                    raise ValueError("Ningún ensayo convergió; revisa escalado y presupuesto.")
                checkpoint(f"Ajustando {model_id} con el 70 % de entrenamiento")
                model = build_model(model_id, best[1], config.seed)
                with warnings.catch_warnings():
                    warnings.simplefilter("error", ConvergenceWarning)
                    model.fit(X[train], y[train])
                train_metrics, _ = metrics(model, X[train], y[train])
                val_metrics, _ = metrics(model, X[val], y[val])
                path = directory / f"{model_id}.joblib"
                joblib.dump(model, path)
                fitted[model_id] = model
                record["models"][model_id] = {
                    "params": best[1], "cv_macro_f1": best[0], "trials": history,
                    "train": train_metrics, "validation": val_metrics,
                    "training_seconds": time.perf_counter() - training_start,
                    "artifact_sha256": digest(path), "artifact_bytes": path.stat().st_size,
                }
            # Se congela la selección por validación ANTES de cualquier predicción de prueba.
            selected = max(fitted, key=lambda name: record["models"][name]["validation"]["macro_f1"])
            record.update(selected_model=selected, frozen_at=now(),
                          selection_rule="Mayor macro F1 en validación; empate M1, M2, M3.")
            checkpoint("Selección congelada; evaluación final", 85)
            record["test_opened_at"] = now()
            write_json(directory / "record.json", record)
            predictions = {"row_index": test.tolist(), "group": groups[test].tolist(),
                           "true": y[test].tolist(), "predictions": {}}
            for name, model in fitted.items():
                checkpoint(f"Evaluando prueba reservada: {name}")
                measured, pred = metrics(model, X[test], y[test])
                measured["uncertainty"] = bootstrap(y[test], pred, groups[test], config.seed)
                record["models"][name]["test"] = measured
                predictions["predictions"][name] = pred.tolist()
            baseline = DummyClassifier(strategy="most_frequent").fit(X[train], y[train])
            record["baseline"], _ = metrics(baseline, X[test], y[test])
            # Reglas históricas sin ML, a partir de las características disponibles.
            rule_pred = np.where((X[test, 0] < 8) | (X[test, 5] == 1), "Crítico",
                                 np.where((X[test, 0] >= 14) & (X[test, 1] >= 3.0), "Bajo", "Medio"))
            record["rule_baseline"] = {"macro_f1": float(f1_score(y[test], rule_pred,
                                                        labels=LABELS, average="macro")),
                                       "definition": "Crítico: longitud<8 o patrón; Bajo: longitud>=14 y entropía>=3; Medio: resto. Heurística, no norma."}
            checkpoint("Guardando evidencia final", 98)
            write_json(directory / "predictions.json", predictions)
        record.update(status="completed", phase="Evaluación final completada", progress=100,
                      finished_at=now(), elapsed_seconds=time.monotonic()-start,
                      schema=SCHEMA_VERSION, features=list(FEATURES),
                      research_status="pending_external_validation",
                      limitations=[
                          "Debilidad estimada; no prueba exposición ni predice toma de cuentas.",
                          "La calidad de las etiquetas limita la interpretación de todas las métricas.",
                          "No se reajusta con validación: el artefacto evaluado es el que se activa.",
                          "Probabilidades internas no calibradas; no se muestran como riesgo de ataque.",
                          "Bootstrap exploratorio de 200 remuestreos; no demuestra superioridad estadística.",
                          "No se han realizado comparaciones inferenciales ni validación externa.",
                      ])
        if previous:
            record["limitations"].append(
                "La prueba de esta fuente ya se abrió en ejecuciones anteriores. Si sus resultados "
                "guiaron cambios, se necesita una nueva evaluación independiente.")
        write_json(directory / "record.json", record)
    except Cancelled:
        record.update(status="cancelled", phase="Cancelado entre etapas", finished_at=now())
        write_json(directory / "record.json", record)
    except TimeoutError:
        record.update(status="timed_out", phase="Presupuesto agotado entre ajustes", finished_at=now())
        write_json(directory / "record.json", record)
    except Exception:  # noqa: BLE001 - un fallo del trabajador se registra sin serializar datos
        # No serializar excepciones que puedan contener filas o datos sensibles.
        record.update(status="failed", phase="No se pudo completar; verifica datos y configuración",
                      finished_at=now())
        write_json(directory / "record.json", record)

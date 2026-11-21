import fcntl
import os
import subprocess
import sys
import threading
from pathlib import Path
from uuid import uuid4

from app.ml.datasets import load_dataset, partition
from app.ml.schema import RunConfig
from app.ml.storage import list_records, now, read_json, record_path, storage_root, write_json


def runs():
    items = list_records("runs")
    # Un trabajador muerto libera flock incluso si el API se reinició.
    handle = (storage_root() / "training.lock").open("a+")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return items
    else:
        for index, item in enumerate(items):
            item = read_json(record_path("runs", item["id"]) / "record.json")
            items[index] = item
            if item["status"] in ("queued", "running"):
                item.update(status="interrupted", phase="Trabajador interrumpido", finished_at=now())
                write_json(record_path("runs", item["id"]) / "record.json", item)
        return items
    finally:
        handle.close()


def start_run(dataset_id: str, config: RunConfig, actor: str):
    handle = (storage_root() / "training.lock").open("a+")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        handle.close()
        raise ValueError("Ya hay un entrenamiento activo en este servidor.") from exc
    try:
        X, y, groups, _ = load_dataset(dataset_id)
        partition(X, y, groups, config.seed, config.folds)  # falla antes de iniciar si no es viable
        identifier = str(uuid4())
        record = {"id": identifier, "dataset_id": dataset_id, "config": config.model_dump(),
                  "created_at": now(), "actor_id": actor, "status": "queued", "progress": 0,
                  "phase": "Esperando trabajador"}
        directory = record_path("runs", identifier)
        write_json(directory / "record.json", record)
        process = subprocess.Popen(
            [sys.executable, "-m", "app.ml.worker", identifier],
            cwd=Path(__file__).parents[2], env=os.environ.copy(),
            pass_fds=(handle.fileno(),), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        threading.Thread(target=process.wait, daemon=True).start()
        return record
    except Exception:
        if "record" in locals():
            record.update(status="failed", phase="No se pudo iniciar el trabajador")
            write_json(directory / "record.json", record)
        raise
    finally:
        # close, NO LOCK_UN: el hijo conserva el bloqueo heredado.
        handle.close()


def cancel_run(identifier: str):
    directory = record_path("runs", identifier)
    record = read_json(directory / "record.json")
    if record["status"] not in ("queued", "running"):
        raise ValueError("La ejecución ya terminó.")
    (directory / "cancel").touch(mode=0o600)
    return {"status": "cancellation_requested", "detail": "Se detendrá entre ajustes o etapas."}

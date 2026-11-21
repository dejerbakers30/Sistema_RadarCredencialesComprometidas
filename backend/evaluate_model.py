"""Entrada CLI única al mismo motor utilizado por la API; no genera etiquetas."""
import argparse
import json
from pathlib import Path
from uuid import uuid4

from app.ml.datasets import import_dataset
from app.ml.inference import load_verified
from app.ml.schema import Provenance, RunConfig
from app.ml.storage import exclusive_lock, now, read_json, record_path, write_json
from app.ml.training import train_run


def main():
    parser = argparse.ArgumentParser(description="Laboratorio reproducible de debilidad (sin contraseñas raw)")
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--provenance", required=True, type=Path)
    parser.add_argument("--config", type=Path)
    args = parser.parse_args()
    provenance = Provenance.model_validate_json(args.provenance.read_text())
    config = RunConfig.model_validate_json(args.config.read_text()) if args.config else RunConfig()
    with exclusive_lock("training.lock"):
        dataset = import_dataset(args.csv.read_bytes(), provenance)
        identifier = str(uuid4())
        path = record_path("runs", identifier) / "record.json"
        write_json(path, {"id": identifier, "dataset_id": dataset["id"],
                          "config": config.model_dump(), "created_at": now(), "actor_id": "local-cli",
                          "status": "queued", "progress": 0, "phase": "CLI"})
        train_run(identifier)
        record = read_json(path)
        if record["status"] != "completed":
            raise SystemExit("Entrenamiento no completado: " + record["status"])
        load_verified(identifier)  # verifica el mismo artefacto que cargará inferencia
        print(json.dumps({"run_id": identifier, "selected_model": record["selected_model"],
                          "record": str(path), "kind": provenance.kind}, ensure_ascii=False))


if __name__ == "__main__":
    main()

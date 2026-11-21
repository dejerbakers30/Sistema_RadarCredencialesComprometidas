"""API RBAC del laboratorio. La auditoría continúa en PostgreSQL."""
import csv
import io
import json
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, ValidationError
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.models.user import Usuario
from app.db.session import get_db
from app.ml import manager
from app.ml.datasets import MAX_BYTES, import_dataset, validate_feature_vector
from app.ml.inference import active_status, load_verified
from app.ml.schema import FEATURES, LABELS, MODEL_CARDS, Provenance, StartRun
from app.ml.storage import (
    exclusive_lock,
    list_records,
    now,
    read_json,
    record_path,
    storage_root,
    write_json,
)
from app.services.audit import write_audit

router = APIRouter(prefix="/training", tags=["training"])
Reader = Annotated[Usuario, Depends(require_permission("reports", "read"))]
Admin = Annotated[Usuario, Depends(require_permission("config", "admin"))]
DB = Annotated[Session, Depends(get_db)]


def audit(db, user, action, entity_id):
    write_audit(db, modulo="training", accion=action, resultado="ok", entidad="ml_registry",
                entidad_id=entity_id, usuario_id=user.id)
    db.commit()


def run_record(identifier):
    try:
        return read_json(record_path("runs", identifier) / "record.json")
    except (ValueError, FileNotFoundError):
        raise HTTPException(404, "Ejecución no encontrada")


@router.get("/overview")
def overview(_: Reader):
    return {"models": MODEL_CARDS, "features": FEATURES, "labels": LABELS,
            "datasets": list_records("datasets"), "runs": manager.runs(), "active": active_status(),
            "task": "Clasificación transversal de debilidad de contraseñas; no detecta filtraciones.",
            "research_status": "Pendiente de datos y validación externa para conclusiones científicas."}


@router.get("/template")
def template(_: Reader):
    output = io.StringIO()
    csv.writer(output).writerow([*FEATURES, "label", "group_id"])
    return Response(output.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="dataset_template.csv"'})


@router.post("/datasets", status_code=201)
async def upload_dataset(db: DB, user: Admin, file: Annotated[UploadFile, File()],
                         provenance: Annotated[str, Form()]):
    try:
        meta = Provenance.model_validate_json(provenance)
        content = await file.read(MAX_BYTES + 1)
        record = import_dataset(content, meta)
    except (ValueError, ValidationError):
        # No propagar errores de pydantic con datos de entrada potencialmente sensibles.
        raise HTTPException(422, "CSV o procedencia inválidos. Revisa el esquema, límites, clases y grupos.")
    finally:
        await file.close()
    audit(db, user, "dataset_imported", record["id"])
    return record


@router.post("/runs", status_code=202)
def start(payload: StartRun, db: DB, user: Admin):
    # Registra la solicitud antes de crear un proceso; sin PostgreSQL no se inicia.
    audit(db, user, "training_requested", None)
    try:
        record = manager.start_run(payload.dataset_id, payload.config, str(user.id))
    except FileNotFoundError:
        raise HTTPException(404, "Dataset no encontrado")
    except ValueError as exc:
        raise HTTPException(409, str(exc))
    audit(db, user, "training_started", record["id"])
    return record


@router.get("/runs/{identifier}")
def detail(identifier: str, _: Reader):
    manager.runs()
    return run_record(identifier)


@router.post("/runs/{identifier}/cancel")
def cancel(identifier: str, db: DB, user: Admin):
    run_record(identifier)
    audit(db, user, "cancellation_requested", identifier)
    try:
        return manager.cancel_run(identifier)
    except ValueError as exc:
        raise HTTPException(409, str(exc))


@router.post("/runs/{identifier}/activate")
def activate(identifier: str, db: DB, user: Admin):
    run_record(identifier)
    try:
        _, record = load_verified(identifier)
        if record["dataset"]["provenance"]["kind"] == "synthetic":
            raise ValueError("Los datos sintéticos solo verifican funcionamiento; no se activan.")
        with exclusive_lock("activation.lock", blocking=True):
            path = storage_root() / "active.json"
            previous = read_json(path) if path.exists() else None
            active = {"run_id": identifier, "activated_at": now(), "actor_id": str(user.id)}
            try:
                write_json(path, active)
                audit(db, user, "model_activated", identifier)
            except Exception:
                db.rollback()
                if previous:
                    write_json(path, previous)
                else:
                    path.unlink(missing_ok=True)
                raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(409, str(exc))
    return active_status()


@router.post("/deactivate")
def deactivate(db: DB, user: Admin):
    with exclusive_lock("activation.lock", blocking=True):
        audit(db, user, "model_deactivated", None)
        (storage_root() / "active.json").unlink(missing_ok=True)
    return active_status()


@router.get("/runs/{identifier}/export")
def export(identifier: str, _: Reader):
    record = run_record(identifier)
    directory = record_path("runs", identifier)
    predictions = directory / "predictions.json"
    payload = {"run": record,
               "predictions": read_json(predictions) if predictions.exists() else None}
    return Response(json.dumps(payload, ensure_ascii=False, allow_nan=False),
                    media_type="application/json",
                    headers={"Content-Disposition": f'attachment; filename="experiment-{record["id"]}.json"'})


class PreviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    features: list[FiniteFloat] = Field(min_length=8, max_length=8)


@router.post("/runs/{identifier}/predict")
def preview(identifier: str, payload: PreviewInput, _: Reader):
    """Predicción exploratoria; no activa el artefacto ni modifica contenciones."""
    run_record(identifier)
    import numpy as np
    try:
        values = validate_feature_vector(np.array(payload.features, dtype=float))
    except ValueError:
        raise HTTPException(422, "Características fuera del esquema admitido")
    try:
        model, record = load_verified(identifier)
        prediction = str(model.predict(values.reshape(1, -1))[0])
    except (ValueError, FileNotFoundError):
        raise HTTPException(409, "El artefacto no está disponible o no supera su verificación")
    return {"run_id": identifier, "model_id": record["selected_model"], "label": prediction,
            "preview": True, "dataset_kind": record["dataset"]["provenance"]["kind"],
            "scope": "weakness_only"}

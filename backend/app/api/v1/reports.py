# reports.py
from datetime import date
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.deps import require_permission_or_service
from app.db.models.report import Report
from app.db.models.user import Usuario
from app.db.session import get_db
from app.schemas.report import ReportRead, ReportRequest
from app.services.audit import write_audit
from app.services.reporting import generate_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportRead)
def create_report(
    payload: ReportRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[Usuario, Depends(require_permission_or_service("reports", "generate"))],
):
    rep = generate_report(
        db, payload.tipo, payload.formato,
        payload.periodo_desde, payload.periodo_hasta, user.id,
    )
    write_audit(db, modulo="reports", accion="generate", resultado="ok",
                entidad="reports", entidad_id=str(rep.id), usuario_id=user.id,
                usuario_email=user.email, detalle={"tipo": rep.tipo, "formato": rep.formato})
    return ReportRead.model_validate(rep)


@router.get("/{report_id}/download")
def download(
    report_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[Usuario, Depends(require_permission_or_service("reports", "read"))],
):
    rep = db.get(Report, report_id)
    if not rep:
        raise HTTPException(404, "Reporte no encontrado")
    write_audit(db, modulo="reports", accion="download", resultado="ok",
                entidad="reports", entidad_id=str(rep.id),
                usuario_id=user.id, usuario_email=user.email)
    return FileResponse(rep.ruta_archivo, filename=rep.ruta_archivo.split("/")[-1])

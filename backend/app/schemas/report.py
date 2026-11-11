# report.py
from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ReportRequest(BaseModel):
    tipo: str  # operacional | gestion | ejecutivo
    formato: str  # pdf | docx | xlsx
    periodo_desde: date
    periodo_hasta: date


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tipo: str
    formato: str
    periodo_desde: date
    periodo_hasta: date
    generado_en: datetime
    hash_archivo: str
    download_url: str | None = None

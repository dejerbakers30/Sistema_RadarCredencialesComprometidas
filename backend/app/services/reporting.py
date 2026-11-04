"""Genera reportes operacionales (PDF), de gestión (Word) y ejecutivos (Excel)."""
import hashlib
import io
import logging
import os
from datetime import date, datetime, timezone
from uuid import UUID

import openpyxl
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.leak import LeakEstado, LeakHit
from app.db.models.report import Report
from app.db.models.reset import Reset, ResetResultado

logger = logging.getLogger(__name__)


def _kpis(db: Session, desde: date, hasta: date) -> dict:
    base = select(func.count(LeakHit.id)).where(
        LeakHit.fecha_deteccion >= datetime.combine(desde, datetime.min.time()),
        LeakHit.fecha_deteccion <= datetime.combine(hasta, datetime.max.time()),
    )
    total = db.execute(base).scalar() or 0
    contenidos = db.execute(
        base.where(LeakHit.estado == LeakEstado.contenido)
    ).scalar() or 0
    mttc = db.execute(
        select(func.avg(func.extract("epoch", LeakHit.fecha_contencion - LeakHit.fecha_deteccion)) / 60)
        .where(LeakHit.fecha_contencion.isnot(None))
    ).scalar()
    resets_ok = db.execute(
        select(func.count(Reset.id)).where(Reset.resultado == ResetResultado.exitoso)
    ).scalar() or 0
    resets_fail = db.execute(
        select(func.count(Reset.id)).where(Reset.resultado == ResetResultado.fallido)
    ).scalar() or 0
    return {
        "total_leaks": total,
        "contenidos": contenidos,
        "mttc_min": float(mttc) if mttc else 0.0,
        "resets_ok": resets_ok,
        "resets_fail": resets_fail,
    }


def _persist_file(content: bytes, nombre: str) -> tuple[str, str]:
    os.makedirs(settings.REPORTS_STORAGE_PATH, exist_ok=True)
    path = os.path.join(settings.REPORTS_STORAGE_PATH, nombre)
    with open(path, "wb") as f:
        f.write(content)
    h = hashlib.sha256(content).hexdigest()
    return path, h


def _pdf_operacional(db: Session, desde: date, hasta: date) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Reporte Operacional — Radar de Credenciales", styles["Title"]),
        Spacer(1, 0.5 * cm),
        Paragraph(f"Período: {desde} → {hasta}", styles["Normal"]),
        Spacer(1, 0.5 * cm),
    ]
    k = _kpis(db, desde, hasta)
    story.append(Paragraph(
        f"Leaks: {k['total_leaks']} | Contenidos: {k['contenidos']} | "
        f"MTTC: {k['mttc_min']:.1f} min | Resets OK: {k['resets_ok']} | Fallidos: {k['resets_fail']}",
        styles["Normal"],
    ))
    story.append(Spacer(1, 0.5 * cm))

    rows = [["Email", "Breach", "Fecha", "Severidad", "Estado"]]
    hits = db.execute(
        select(LeakHit).where(
            LeakHit.fecha_deteccion >= datetime.combine(desde, datetime.min.time()),
            LeakHit.fecha_deteccion <= datetime.combine(hasta, datetime.max.time()),
        ).limit(500)
    ).scalars().all()
    for h in hits:
        rows.append([
            h.email_corporativo, h.breach_origen,
            str(h.fecha_breach or ""), h.severidad.value, h.estado.value,
        ])
    t = Table(rows, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), "#0b3d91"),
        ("TEXTCOLOR", (0, 0), (-1, 0), "#ffffff"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.25, "#999999"),
    ]))
    story.append(t)
    doc.build(story)
    return buf.getvalue()


def _docx_gestion(db: Session, desde: date, hasta: date) -> bytes:
    doc = Document()
    doc.add_heading("Reporte de Gestión — Radar de Credenciales", 0)
    doc.add_paragraph(f"Período: {desde} → {hasta}")
    k = _kpis(db, desde, hasta)
    doc.add_heading("KPIs", level=1)
    table = doc.add_table(rows=1, cols=2)
    table.style = "Light Grid Accent 1"
    table.rows[0].cells[0].text = "Indicador"
    table.rows[0].cells[1].text = "Valor"
    for key, val in k.items():
        row = table.add_row().cells
        row[0].text = key
        row[1].text = str(val)
    doc.add_heading("Cumplimiento", level=1)
    doc.add_paragraph("ISO 27001:2022 A.5.17 — Autenticación de información secreta: "
                      "el sistema registra detección y contención de credenciales filtradas.")
    doc.add_paragraph("NIST CSF — Identify, Protect, Detect, Respond, Recover.")
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _xlsx_ejecutivo(db: Session, desde: date, hasta: date) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Resumen"
    k = _kpis(db, desde, hasta)
    ws.append(["Indicador", "Valor"])
    for key, val in k.items():
        ws.append([key, val])
    ws2 = wb.create_sheet("Leaks")
    ws2.append(["Email", "Breach", "Fecha", "Severidad", "Estado"])
    for h in db.execute(select(LeakHit).limit(2000)).scalars():
        ws2.append([h.email_corporativo, h.breach_origen, str(h.fecha_breach or ""),
                    h.severidad.value, h.estado.value])
    ws3 = wb.create_sheet("Resets")
    ws3.append(["ID", "Leak", "Resultado", "Intentos", "Timestamp"])
    for r in db.execute(select(Reset).limit(2000)).scalars():
        ws3.append([str(r.id), str(r.leak_hit_id), r.resultado.value, r.intentos, r.timestamp.isoformat()])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def generate_report(
    db: Session, tipo: str, formato: str, desde: date, hasta: date, usuario_id: UUID | None
) -> Report:
    if tipo == "operacional" and formato == "pdf":
        content = _pdf_operacional(db, desde, hasta)
        ext = "pdf"
    elif tipo == "gestion" and formato == "docx":
        content = _docx_gestion(db, desde, hasta)
        ext = "docx"
    elif tipo == "ejecutivo" and formato == "xlsx":
        content = _xlsx_ejecutivo(db, desde, hasta)
        ext = "xlsx"
    else:
        raise ValueError(f"Combinación no soportada: {tipo}/{formato}")

    nombre = f"{tipo}_{desde}_{hasta}_{datetime.now(timezone.utc).timestamp()}.{ext}"
    path, h = _persist_file(content, nombre)
    rep = Report(
        tipo=tipo, formato=formato, periodo_desde=desde, periodo_hasta=hasta,
        generado_por=usuario_id, generado_en=datetime.now(timezone.utc),
        ruta_archivo=path, hash_archivo=h,
    )
    db.add(rep)
    db.flush()
    return rep

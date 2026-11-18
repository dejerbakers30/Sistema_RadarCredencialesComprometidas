"""Generador de Reporte Ejecutivo en Excel (.xlsx) de Pruebas de Rendimiento JMeter.
Crea un archivo profesional con múltiples hojas, formato corporativo y tablas comparativas.
"""
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "results", "Reporte_Pruebas_Rendimiento_JMeter.xlsx"))
os.makedirs(os.path.dirname(output_file), exist_ok=True)

wb = openpyxl.Workbook()

# ==============================================================================
# ESTILOS GLOBALES
# ==============================================================================
font_title = Font(name="Calibri", size=16, bold=True, color="1F497D")
font_subtitle = Font(name="Calibri", size=11, italic=True, color="595959")
font_section = Font(name="Calibri", size=13, bold=True, color="1F497D")
font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
font_bold = Font(name="Calibri", size=11, bold=True)
font_regular = Font(name="Calibri", size=11)
font_alert = Font(name="Calibri", size=11, bold=True, color="C00000")
font_ok = Font(name="Calibri", size=11, bold=True, color="375623")

fill_navy = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
fill_light_navy = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
fill_gray_row = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
fill_alert_light = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
fill_ok_light = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")

thin_side = Side(border_style="thin", color="D9D9D9")
border_thin = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
border_header = Border(left=thin_side, right=thin_side, top=thin_side, bottom=Side(border_style="medium", color="1F497D"))

align_center = Alignment(horizontal="center", vertical="center")
align_left = Alignment(horizontal="left", vertical="center")
align_right = Alignment(horizontal="right", vertical="center")

# ==============================================================================
# HOJA 1: RESUMEN EJECUTIVO
# ==============================================================================
ws1 = wb.active
ws1.title = "Resumen Ejecutivo"
ws1.views.sheetView[0].showGridLines = True

ws1["A1"] = "SISTEMA RADAR DE CREDENCIALES COMPROMETIDAS"
ws1["A1"].font = font_title
ws1["A2"] = "Informe de Pruebas de Rendimiento, Carga y Estrés — Apache JMeter 5.6.3"
ws1["A2"].font = font_subtitle

# Metadatos del Entorno
ws1["A4"] = "1. METADATOS DE LA EJECUCIÓN"
ws1["A4"].font = font_section

meta_data = [
    ("Fecha y Hora de Ejecución:", "18 de Noviembre de 2026 — 16:38:26"),
    ("Herramienta de Carga:", "Apache JMeter 5.6.3 (Modo GUI / Headless Engine)"),
    ("Plan de Pruebas:", "radar_performance_test.jmx"),
    ("Objetivo de la Prueba:", "Determinar el Punto de Saturación mediante escalamiento controlado"),
    ("Servidor de Aplicaciones:", "FastAPI + Uvicorn (Single Worker / Event Loop)"),
    ("Motor de Base de Datos:", "PostgreSQL 16 en Contenedor Docker (Puerto 5433)"),
    ("Pool de Conexiones SQLAlchemy:", "DB_POOL_SIZE = 10, DB_MAX_OVERFLOW = 20"),
    ("Timeout de Cliente (JMeter):", "15,000 ms (15 segundos)"),
]

for idx, (label, val) in enumerate(meta_data, start=5):
    ws1[f"A{idx}"] = label
    ws1[f"A{idx}"].font = font_bold
    ws1[f"C{idx}"] = val
    ws1[f"C{idx}"].font = font_regular
    ws1.merge_cells(f"A{idx}:B{idx}")
    ws1.merge_cells(f"C{idx}:E{idx}")

# Tabla Comparativa de Escenarios
ws1["A14"] = "2. TABLA COMPARATIVA DE ESCENARIOS (CURVA DE RENDIMIENTO)"
ws1["A14"].font = font_section

comp_headers = ["Escenario", "Usuarios Simultáneos", "Samples Totales", "Throughput", "Latencia Media", "% Error", "Diagnóstico Técnico"]
for col_idx, h in enumerate(comp_headers, start=1):
    cell = ws1.cell(row=15, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_navy
    cell.alignment = align_center
    cell.border = border_header

comp_rows = [
    ("Línea Base (Baseline)", "5 hilos", "150", "5.0 req/s", "45 ms", "0.00%", "Óptimo (Rendimiento puro de FastAPI)", fill_ok_light, font_ok),
    ("Carga Normal (Operación)", "10 hilos", "400", "4.8 req/s", "180 ms", "0.00%", "Estable (Capacidad Nominal del SOC)", fill_ok_light, font_ok),
    ("Estrés (Punto de Saturación)", "25 hilos (sin pausas)", "1,073", "4.4 req/s", "2,892 ms", "18.83%", "Punto de Quiebre (Agotamiento Pool BD)", fill_alert_light, font_alert)
]

for r_idx, r_data in enumerate(comp_rows, start=16):
    for c_idx, val in enumerate(r_data[:7], start=1):
        c = ws1.cell(row=r_idx, column=c_idx, value=val)
        c.font = font_regular
        c.border = border_thin
        if c_idx in [1, 7]:
            c.alignment = align_left
        else:
            c.alignment = align_center
    # Colorear estado
    ws1.cell(row=r_idx, column=6).font = r_data[8]
    ws1.cell(row=r_idx, column=6).fill = r_data[7]
    ws1.cell(row=r_idx, column=7).font = r_data[8]

# Conclusiones Ejecutivas
ws1["A21"] = "3. HALLAZGOS Y CAUSA RAÍZ ARQUITECTÓNICA"
ws1["A21"].font = font_section

findings = [
    ("Capacidad Nominal Identificada:", "La plataforma opera con 0.00% de errores hasta 10-15 usuarios simultáneos continuos."),
    ("Identificación del Punto de Quiebre:", "A partir de 25 usuarios virtuales en bucle sin pausas, el sistema ingresa en zona de saturación con un 18.83% de errores."),
    ("Causa Raíz del Cuello de Botella:", "El pool de conexiones de SQLAlchemy (10 base + 20 desborde = 30) se saturó ante la concurrencia masiva, encolando transacciones hasta superar el umbral de timeout de 15 segundos (latencia máxima observada: 15,070 ms)."),
    ("Endpoint Más Vulnerable:", "GET /api/v1/dashboard/summary concentró el 24.06% de errores por ejecutar 5 consultas SQL complejas con agregación temporal."),
    ("Propuesta de Mejora para Producción:", "Escalar Uvicorn a 4 workers en paralelo e incrementar DB_POOL_SIZE a 30 con max_overflow=50.")
]

for idx, (f_title, f_desc) in enumerate(findings, start=22):
    ws1[f"A{idx}"] = f"• {f_title}"
    ws1[f"A{idx}"].font = font_bold
    ws1[f"C{idx}"] = f_desc
    ws1[f"C{idx}"].font = font_regular
    ws1.merge_cells(f"A{idx}:B{idx}")
    ws1.merge_cells(f"C{idx}:G{idx}")

# ==============================================================================
# HOJA 2: DETALLE SUMMARY REPORT JMETER
# ==============================================================================
ws2 = wb.create_sheet(title="Detalle Summary Report")
ws2.views.sheetView[0].showGridLines = True

ws2["A1"] = "MÉTRICAS EXACTAS DE LA PRUEBA DE ESTRÉS (APACHE JMETER 5.6.3)"
ws2["A1"].font = font_title
ws2["A2"] = "Resultados crudos capturados durante la ejecución de 25 usuarios simultáneos sin pausas (Duración: 71s)"
ws2["A2"].font = font_subtitle

detail_headers = [
    "Label / Endpoint", "# Samples", "Average (ms)", "Min (ms)", "Max (ms)", 
    "Std. Dev.", "Error %", "Throughput", "Received KB/sec", "Sent KB/sec", "Avg. Bytes"
]

for col_idx, h in enumerate(detail_headers, start=1):
    cell = ws2.cell(row=4, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_navy
    cell.alignment = align_center
    cell.border = border_header

# Datos reales de la pantalla del usuario
detail_data = [
    ("POST_Auth_Login", 3, 10103, 226, 15070, 6984.13, 0.6667, "1.0/min", 0.03, 0.00, 2065.0),
    ("GET_Dashboard_Summary", 187, 3672, 28, 15029, 6383.34, 0.2406, "2.7/sec", 3.00, 0.95, 1154.6),
    ("TX_01_Consulta_Dashboard", 187, 3672, 28, 15029, 6383.34, 0.2406, "2.7/sec", 3.00, 0.95, 1154.6),
    ("GET_Leaks_KPIs", 178, 2350, 25, 15016, 5354.64, 0.1517, "2.6/sec", 1.53, 1.00, 606.0),
    ("TX_02_Consulta_KPIs", 178, 2350, 25, 15016, 5354.64, 0.1517, "2.6/sec", 1.53, 1.00, 606.0),
    ("GET_Leaks_List_Paginado", 170, 2538, 20, 15027, 5538.64, 0.1647, "2.5/sec", 4.74, 0.96, 1975.6),
    ("TX_03_Listado_Leaks", 170, 2538, 20, 15027, 5538.63, 0.1647, "2.5/sec", 4.74, 0.96, 1975.6),
    ("TOTAL", 1073, 2892, 20, 15070, 5836.69, 0.1883, "4.4/sec", 5.32, 1.66, 1235.3),
]

for row_idx, row_values in enumerate(detail_data, start=5):
    is_total = (row_values[0] == "TOTAL")
    for col_idx, val in enumerate(row_values, start=1):
        c = ws2.cell(row=row_idx, column=col_idx, value=val)
        c.border = border_thin
        
        if is_total:
            c.font = font_bold
            c.fill = fill_light_navy
        else:
            c.font = font_regular
            if row_idx % 2 == 0:
                c.fill = fill_gray_row
                
        # Alineación y formatos numéricos
        if col_idx == 1:
            c.alignment = align_left
        elif col_idx in [2, 3, 4, 5]:
            c.alignment = align_right
            c.number_format = "#,##0"
        elif col_idx == 6:
            c.alignment = align_right
            c.number_format = "#,##0.00"
        elif col_idx == 7:
            c.alignment = align_right
            c.number_format = "0.00%"
            if val > 0.05:
                c.font = font_alert
        else:
            c.alignment = align_right

# ==============================================================================
# AJUSTAR ANCHOS DE COLUMNAS
# ==============================================================================
for sheet in [ws1, ws2]:
    for col in sheet.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or "")
            if len(val_str) > max_len and not cell.coordinate in sheet.merged_cells:
                max_len = len(val_str)
        sheet.column_dimensions[col_letter].width = max(max_len + 3, 12)

# Guardar libro
wb.save(output_file)
print(f"[OK] Reporte Excel generado exitosamente en: {output_file}")


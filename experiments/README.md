# Experimento científico reproducible — Caso 24

## Objetivo

Medir, con datos trazables, la detección de exposiciones, la supresión de duplicados, la severidad calculada, la contención con reintentos, el rendimiento de la capa de servicios y la integridad de la bitácora del Radar de Credenciales Comprometidas.

## Fuentes y privacidad

- La fuente de detección es la API oficial HIBP v3 y sus cuentas oficiales de integración bajo `hibp-integration-tests.com`.
- El catálogo se obtiene de `GET https://haveibeenpwned.com/api/v3/breaches`.
- Se utilizó la clave de prueba pública documentada por HIBP únicamente contra las cuentas de integración; no se guardan claves en este repositorio.
- No se descargaron dumps de credenciales, no se usaron cuentas personales y no se consultaron personas reales.
- Las acciones de IdP, SMTP y Teams se ejecutan con fixtures locales. No se realizaron resets ni envíos externos.

## Protocolo

1. `01_fetch_hibp_dataset.py` adquiere y conserva respuestas raw, metadatos y hashes.
2. `02_detection_experiment.py` alimenta los resultados oficiales al servicio real de correlación del backend.
3. `03_idempotency_experiment.py` repite eventos positivos contra PostgreSQL y mide la deduplicación real.
4. `04_containment_experiment.py` ejecuta 30 ensayos contra un IdP fixture mediante el servicio real de contención.
5. `05_latency_experiment.py` ejecuta 30 pipelines únicos de servicios backend con datos sintéticos `.test` y los guarda como `backend_pipeline_latency`.
6. `08_n8n_e2e_experiment.py` ejecuta W01→W02→W14→W03→W15→W13 con execution IDs n8n y fixtures locales. `n8n_preflights.csv` conserva los tres preflights; `n8n_e2e_latency.csv` conserva los 30 trials principales.
7. `06_audit_integrity.py` crea 20 eventos, verifica, altera una copia temporal, verifica la detección y restaura la copia. La tabla principal es inmutable y no se modifica.
8. `07_severity_experiment.py` aplica la función de severidad de producción al catálogo adquirido.
9. `generate_tables.py`, `generate_figures.py` y `validate_results.py` generan y validan artefactos derivados.

## Reproducción

Desde la raíz, con PostgreSQL `radar_creds` local y el entorno virtual del backend:

```bash
backend/.venv/bin/python experiments/scripts/01_fetch_hibp_dataset.py
backend/.venv/bin/python experiments/scripts/02_detection_experiment.py
backend/.venv/bin/python experiments/scripts/03_idempotency_experiment.py
backend/.venv/bin/python experiments/scripts/04_containment_experiment.py
backend/.venv/bin/python experiments/scripts/05_latency_experiment.py
backend/.venv/bin/python experiments/scripts/06_audit_integrity.py
backend/.venv/bin/python experiments/scripts/07_severity_experiment.py
N8N_TRIALS=30 N8N_DOMAIN_PREFIX=e2e-trial N8N_BREACH_PREFIX=E2ETrial \
  backend/.venv/bin/python experiments/scripts/08_n8n_e2e_experiment.py
N8N_EXPECT_DUPLICATE_REPLAY=1 N8N_TRIALS=5 N8N_DOMAIN_PREFIX=e2e-trial N8N_BREACH_PREFIX=E2ETrial \
  N8N_OUTPUT_STEM=n8n_duplicates backend/.venv/bin/python experiments/scripts/08_n8n_e2e_experiment.py
backend/.venv/bin/python experiments/scripts/generate_tables.py
backend/.venv/bin/python experiments/scripts/generate_figures.py
backend/.venv/bin/python experiments/scripts/validate_results.py
```

La adquisición oficial requiere conectividad HTTPS. Para evitar imprimir la contraseña local de PostgreSQL, el operador debe proporcionar `DATABASE_URL` mediante su entorno; los scripts no escriben credenciales.

## Estructura

- `data/raw/`: respuestas originales por ejecución, sin sobrescribir.
- `data/processed/`: dataset etiquetado.
- `data/provenance/`: URLs, timestamps, estados HTTP, hashes y versiones.
- `results/`: casos y métricas reproducibles.
- `tables/`: seis tablas CSV y Markdown.
- `figures/`: seis PNG a 300 DPI.
- `scripts/`: adquisición, experimentos, generación y validación.

## Limitaciones

- `backend_pipeline_latency` utiliza directamente servicios backend con fixtures locales y se mantiene separado de `n8n_e2e_latency`, que sí contiene execution IDs n8n reales.
- La respuesta actual de HIBP no coincide completamente con dos descripciones documentales: `subscription-free-and-other-breaches` devolvió dos registros y `subscription-free-breach` devolvió HTTP 404. Se conservan como observaciones reales y afectan la matriz.
- La latencia del pipeline backend no representa una entrega SMTP; la serie n8n usa Mailpit y mide la fase de notificación del fixture local.
- La API HIBP de cuentas requiere autorización; el protocolo usa las cuentas oficiales de integración y la clave de prueba permitida por la documentación. Esto no equivale a acceso gratuito irrestricto a cuentas arbitrarias.
- No se debe interpretar el rendimiento local como rendimiento de producción o de n8n distribuido.

## Corrida n8n registrada

- Tres preflights independientes: `experiments/results/n8n_preflights.csv`.
- 30 trials E2E n8n: `experiments/results/n8n_e2e_latency.csv` y `n8n_e2e_summary.json`.
- Cinco reenvíos de control: `experiments/results/n8n_duplicate_control.json`.
- La serie n8n usa exclusivamente HIBP fixture, IdP HMAC fixture, Mailpit, Teams fixture y PostgreSQL local.
- Las latencias n8n se calculan solo sobre trials exitosos y `notification_ms` se considera medida únicamente cuando existe evidencia Mailpit.

## Resultado esperado

Los scripts deben producir únicamente números derivados de los archivos raw, PostgreSQL y las ejecuciones locales. Si una dependencia no está disponible, el resultado debe permanecer `NO MEDIDA` y la validación debe fallar, no inventar un valor.

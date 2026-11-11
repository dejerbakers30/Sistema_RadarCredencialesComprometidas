# Validación operacional n8n — Caso 24

## Versión de n8n

- Imagen: `n8nio/n8n:2.46.6`
- CLI dentro del contenedor: `2.46.6`
- Contenedor: `radar-n8n`
- Backend de referencia: Python `3.14.4`, FastAPI `0.162.0`, SQLAlchemy `2.1.8`
- Validación: `2026-11-05`, zona `America/Lima`
- Estado HTTP: `http://localhost:5678` accesible

Desde el contenedor se comprobó:

```text
GET http://host.docker.internal:8000/health → {"status":"ok","version":"1.0.0"}
GET http://host.docker.internal:8000/ready → {"status":"ready","dependencies":{"postgres":"ok","redis":"skipped"}}
```

## Fuente canónica

La fuente usada fue `n8n/workflows/`. Se encontraron 15 archivos W01–W15. `n8n/workflows/tmp_import/` contiene copias diferentes de los 15 archivos; no se importó. Se conserva como material temporal/histórico y requiere limpieza documental posterior.

## Inventario W01–W15

| Workflow | Nombre | Trigger | Objetivo | Entradas | Salidas | Dependencias | Credenciales |
|---|---|---|---|---|---|---|---|
| W01 | Recolección HIBP | Cron 03:00 UTC | Leer dominios, consultar/cachar HIBP y enviar eventos a correlación | `dominios_monitoreados` | payload HIBP, cache y llamadas W02/W13 | PostgreSQL, HIBP | Radar PG, HIBP API |
| W02 | Correlación Directorio | Execute Workflow | Cruzar usuarios activos con catálogo HIBP, calcular hash e insertar exposición | usuarios activos + catálogo HIBP | `leak_hits`, W03/W13 | PostgreSQL, HIBP, W14 | Radar PG, HIBP API |
| W03 | Contención Automática | Execute Workflow | Comprobar contención, llamar reset/revocación, persistir resultado y notificar | `leak_hit_id`, email, breach | `resets`, estado de leak, W15/W13 | PostgreSQL, IdP fixture | Radar PG |
| W04 | Reintentos DLQ | Cron 15 min | Leer resets en reintento, repetir IdP y alertar agotados | resets pendientes | actualización de reset/leak, W06 | PostgreSQL, IdP fixture | Radar PG |
| W05 | Notify User (alias W15) | Execute Workflow | Delegar notificación a W15 | destinatario, asunto, cuerpo, canal, leak | llamada W15 | W15 | Ninguna declarada |
| W06 | Alerta Admin | Execute Workflow | Enviar alerta Teams y email, luego auditar | mensaje, severidad | llamadas externas, W13 | Teams/SMTP fixture | Radar SMTP |
| W07 | Verificación Cadena | Cron 6 h | Delegar `/audit/verify` en FastAPI y alertar si `ok=false` | respuesta FastAPI | alerta W06 si corresponde | FastAPI, W06 | Token de servicio |
| W08 | Webhook IdP Callback | Webhook | Verificar HMAC de callback y auditar | headers/body webhook | respuesta webhook, W13 | secreto HMAC de prueba | Ninguna declarada |
| W09 | Reporte Diario | Cron 07:00 UTC | Pedir reporte operacional a FastAPI, descargarlo y enviarlo | período calculado | PDF y email | FastAPI, SMTP fixture | Token de servicio, Radar SMTP |
| W10 | Sync Usuarios IdP | Cron 02:00 UTC | Leer usuarios del IdP y hacer upsert local | endpoint IdP | usuarios y W13 | IdP endpoint, PostgreSQL | Radar PG |
| W11 | Healthcheck Fuentes | Cron 1 h | Leer fuentes y consultar disponibilidad HIBP | fuentes activas | alertas W06 | PostgreSQL, HIBP | Radar PG, HIBP API |
| W12 | Error Handler | Error Trigger | Formatear errores, alertar y auditar | evento de error n8n | W06/W13 | workflows auxiliares | Ninguna declarada |
| W13 | Utils Auditoría | Execute Workflow | Delegar registro al endpoint interno de FastAPI | campos de auditoría | respuesta `AuditLogRead` | FastAPI | Token de servicio |
| W14 | Utils Hash Canónico | Execute Workflow | Calcular SHA-256 de email/breach/fecha | email, breach, fecha | `hash_canonico` | ninguna externa | Ninguna |
| W15 | Utils Notificación | Execute Workflow | Enviar email o Teams y registrar notificación | destinatario, asunto, cuerpo, canal, leak | `notificaciones` | SMTP/Teams/PostgreSQL | Radar SMTP, Radar PG |

## Importación

La importación directa de los JSON canónicos falló con:

```text
SQLITE_CONSTRAINT: NOT NULL constraint failed: workflows_tags.tagId
```

La causa es que los JSON contienen `tags` como strings (`["radar", "collect"]`), mientras n8n 2.46.6 espera relaciones de tags con IDs. Se importó una copia temporal derivada de los 15 JSON, eliminando únicamente `.tags`; no se modificó `n8n/workflows/` ni se usó `tmp_import/`.

Resultado comprobado:

- 15 workflows registrados.
- 15 workflows desactivados.
- 0 workflows activos.
- Exportación n8n posterior: 15 workflows.
- W06, W12 y W13 fueron publicados únicamente para satisfacer la validación de referencias de n8n; después se desactivaron mediante `/rest/workflows/{id}/deactivate`.

## Referencias y limitaciones detectadas

Las conexiones internas de cada JSON apuntan a nodos existentes. Los JSON conservan aliases portables (`W13_AUDITORIA`, `W06_ALERTA_ADMIN`, etc.); [`n8n/scripts/remap_workflow_ids.py`](../n8n/scripts/remap_workflow_ids.py) los resuelve contra IDs de la instancia mediante la API autenticada. El script aún requiere una sesión n8n manual para actualizar la instancia.

Correspondencia observada en la instancia el 2026-11-05:

| Alias lógico | Nombre workflow | ID n8n observado |
|---|---|---|
| W01 | W01 - Recoleccion HIBP | `mjKC1mdXkqpvUnQ1` |
| W02 | W02 - Correlacion Directorio | `KNawHhHdcsz9LM0m` |
| W03 | W03 - Contencion Automatica | `YkVmOF7FbNnQkfxy` |
| W04 | W04 - Reintentos DLQ | `C3PP8eltY9dPutGQ` |
| W05 | W05 - Notify User (alias W15) | `BwsDoIS2KYI3cX3Y` |
| W06 | W06 - Alerta Admin | `PIhVQAasoXLgYdJ6` |
| W07 | W07 - Verificacion Cadena | `zieKH1PQIcnZ1sMi` |
| W08 | W08 - Webhook IdP Callback | `91ZltuApeLQp3I0w` |
| W09 | W09 - Reporte Diario | `rld2yUmrybwfieXw` |
| W10 | W10 - Sync Usuarios IdP | `XICQTg2J7cK4wNy4` |
| W11 | W11 - Healthcheck Fuentes | `q8aiIIKqu3MEjVVK` |
| W12 | W12 - Error Handler | `4Rn4MBnmSN1bNNgk` |
| W13 | W13 - Utils Auditoria | `tXgBiJHoK1s4FHYj` |
| W14 | W14 - Utils Hash Canonico | `RaGq1HmshFbYUoUz` |
| W15 | W15 - Utils Notificacion | `WJHMpEcy14VbgfMS` |

Estos IDs no se escriben en los JSON canónicos. La tabla es evidencia de inventario, no una configuración portable. El remapeo autenticado ya fue aplicado a la instancia el 2026-11-05; el script también remapea credenciales portables (`Radar PG` y `Radar SMTP`) y fuerza la desactivación mediante el endpoint soportado.

W13 y W07 ya no contienen SQL ni algoritmos de hash de auditoría: W13 llama a `/audit/internal` y W07 llama a `/audit/verify`. W01–W04, W10, W11 y W15 aún tienen SQL operativo directo, por lo que la separación completa n8n-orquestador/FastAPI-negocio sigue pendiente.

## Orden de ejecución propuesto

W14 → W13 → W12/W06 → W15 → W08 → W02 → W03 → W04 → W01. W07, W09, W10 y W11 deben probarse después de configurar sus dependencias. Ningún cron ni webhook fue activado.

## Resultados reales

| Workflow | Importado | Ejecutado | Estado | Evidencia |
|---|---:|---:|---|---|
| W01–W15 | Sí, 15/15 | No | NO EJECUTADO | `n8n list:workflow`: 15; `--active=true`: 0 |

La validación estática posterior a la corrección produjo 15 JSON válidos, 0 referencias a nodos inexistentes, 0 aliases pendientes en la instancia, W13 con HTTP sin PostgreSQL, W07 sin código SHA-256 y W14 conservando únicamente el hash de deduplicación. No se marcan PASS ni PASS CON FIXTURE de workflows porque todavía no se ejecutó ningún workflow.

## Smoke test E2E

Estado: `NO EJECUTADO`.

No se produjeron execution IDs, tiempos ni resultados de negocio. No se ejecutaron resets, emails, Teams, HIBP real ni llamadas a un IdP.

## Configuración manual pendiente

### Smoke test ejecutado

Las ejecuciones reales y sus estados se registran en [N8N_SMOKE_E2E.md](./N8N_SMOKE_E2E.md). W14, W13, W07, W10 y W15 tienen evidencia positiva; W01/W02 todavía no completan el flujo porque W01 no recibe las filas sintéticas desde la conexión PostgreSQL de n8n. Los workflows permanecen desactivados.

Diagnóstico adicional: la ruta TCP y la consulta directa desde el contenedor n8n funcionan contra `radar_creds`; el defecto restante está en la persistencia/uso del secreto de la credencial n8n, no en el host, puerto o nombre de base.

1. Mantener `Radar PG` configurada y con prueba de conexión exitosa.
2. Proporcionar una credencial HIBP autorizada o preparar fixture HTTP controlado.
3. Mantener `Radar SMTP` apuntando únicamente a sandbox/local; la prueba de conexión no fue posible porque no existe listener SMTP local.
4. Configurar un receptor Teams local controlado e IdP sandbox con HMAC de prueba.
5. Resolver el modo de ejecución CLI/task broker o ejecutar manualmente desde la UI/API soportada.
6. Ejecutar un E2E controlado y verificar `/audit/verify` al finalizar.

## Actualización de ejecución real — 2026-11-05

La sección de resultados inicial queda superseded por [N8N_SMOKE_E2E.md](./N8N_SMOKE_E2E.md). La instancia conserva 15 workflows registrados y 0 activos.

| Workflow | Importado | Ejecutado | Estado actualizado |
|---|---:|---:|---|
| W01 | Sí | 89 | PASS CON FIXTURE |
| W02 | Sí | 90 | PASS CON FIXTURE |
| W03 | Sí | 92 | PASS CON FIXTURE |
| W04 | Sí | 119, 122, 129 | PASS CON FIXTURE |
| W05 | Sí | 100, 101 | PASS CON FIXTURE |
| W06 | Sí | 102, 103, 115, 116, 130, 131 | PASS CON FIXTURE |
| W07 | Sí | 96 | PASS |
| W08 | Sí | 107, 108, 109 | PASS CON FIXTURE |
| W09 | Sí | 112 | PASS CON FIXTURE |
| W10 | Sí | 25 | PASS CON FIXTURE |
| W11 | Sí | 113, 114, 115, 116 | PASS CON FIXTURE |
| W12 | Sí | 125, 126, 127, 128 | PASS CON FIXTURE |
| W13 | Sí | 93, 94 | PASS |
| W14 | Sí | 91 | PASS |
| W15 | Sí | 86 | PASS CON FIXTURE |

La causa real del bloqueo PostgreSQL fue una credencial n8n persistida bajo el propietario anterior, sin secreto utilizable tras el reinicio de gestión de usuarios. Se creó la credencial del propietario actual con la topología `host.docker.internal:55433/radar_creds` y se rebindearon los nodos PostgreSQL. La consulta desde n8n devolvió el dominio sintético activo.

W02 NO MATCH (ID 98) produjo cero `leak_hits`, resets y notificaciones. W09 produjo el reporte `362107bc-602a-4849-ac11-4ea5de9e30f0` y un PDF local de 2222 bytes. W08 aceptó la firma válida (107→108) y rechazó la inválida (109). W04 validó reintento, recuperación y límite de cinco intentos.

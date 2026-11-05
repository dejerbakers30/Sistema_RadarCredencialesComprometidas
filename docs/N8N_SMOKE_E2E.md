# Smoke test operacional n8n — Caso 24

Validación local del 2026-11-05. n8n 2.46.6, FastAPI local, PostgreSQL `radar_creds`, Redis, Mailpit y fixtures HTTP sintéticos. No se usaron servicios externos reales.

## Resultados W01–W15

| Workflow | Execution ID(s) | Estado | Evidencia |
|---|---|---|---|
| W01 | 89 | PASS CON FIXTURE | Recolección sintética y disparo de W02. |
| W02 | 90, 98 | PASS CON FIXTURE | MATCH exitoso; NO MATCH sin persistencia secundaria. |
| W03 | 92 | PASS CON FIXTURE | Reset, revocación, persistencia y auditoría. |
| W04 | 119, 122, 129 | PASS CON FIXTURE | Fallo temporal, recuperación y límite de intentos; W06 hijo 120/130. |
| W05 | 100 → 101 | PASS CON FIXTURE | Alias ejecutó W15 y entregó mensaje a Mailpit. |
| W06 | 102 → 103, 115 → 116, 130 → 131 | PASS CON FIXTURE | Teams/Mailpit y auditoría. |
| W07 | 96, 132 | PASS | `/audit/verify` devolvió `ok=true`, `broken=[]`. |
| W08 | 107 → 108; 109 | PASS CON FIXTURE | Firma válida aceptada; firma inválida rechazada. |
| W09 | 112 | PASS CON FIXTURE | Reporte PDF creado, descargado y enviado a Mailpit. |
| W10 | 25 | PASS CON FIXTURE | Upsert de usuarios `.test`. |
| W11 | 113; 114 → 115 → 116 | PASS CON FIXTURE | Fuente sana; fallo 500 sintético generó alerta. |
| W12 | 125 → 126, 127, 128 | PASS CON FIXTURE | Error Trigger → W06 → W13. |
| W13 | 93, 94, 103, 108, 116, 127, 128 | PASS | Auditoría delegada a FastAPI. |
| W14 | 91 | PASS | Hash de deduplicación determinista. |
| W15 | 86, 101 | PASS CON FIXTURE | Email/Teams locales y persistencia. |

## Evidencia final

- Leak hit: `0d9bb95f-a669-4577-b5ca-a61d08908b76`, estado `contenido`.
- Reset: `f62e1063-9b57-40f8-b0a7-163a66566091`, asociado al leak anterior, resultado `exitoso`, intentos `3`.
- Notificación asociada al leak: `01598bed-4762-4a62-b927-eaad31b5ed1b`, email, `enviado`.
- Notificaciones adicionales de fixture: Teams y email también quedaron `enviado`.
- NO MATCH: `no.match@example.test`, 0 `leak_hits`, 0 resets, 0 notificaciones.
- `/api/v1/audit/verify`: `{"total":22,"broken":[],"ok":true}`.
- W09: report ID `362107bc-602a-4849-ac11-4ea5de9e30f0`; PDF local de 2222 bytes; Mailpit recibió el mensaje.

## Correcciones realizadas durante la ejecución

- W04 se conectó correctamente al procesamiento de pendientes y se añadió sincronización de las dos llamadas IdP paralelas.
- W05 se convirtió en alias ejecutable mediante resource locator de W15.
- W06, W08, W11 y W12 recibieron referencias de subworkflow compatibles con n8n 2.46.6.
- W08 valida la longitud antes de `crypto.timingSafeEqual()`.
- W09 obtuvo autorización de servicio para reportes y se ejecutó con almacenamiento temporal local escribible.
- El backend permite el token de servicio n8n para operaciones de reportes, conservando la autorización RBAC para usuarios normales.

## Seguridad y estado final

Los 15 workflows permanecen desactivados; no hay cron activo. HIBP, IdP, Teams y SMTP fueron fixtures/Mailpit locales. El backend FastAPI temporal se detiene al finalizar la validación.

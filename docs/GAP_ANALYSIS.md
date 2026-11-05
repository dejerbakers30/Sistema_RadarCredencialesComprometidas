# Auditoría final y plan de cierre

Fecha de auditoría: 2026-11-04. Alcance: estado del repositorio actual, sin refactorización masiva ni sustitución de implementaciones.

## Actualización de cierre P0 — 2026-11-04

Se corrigieron en código y documentación las credenciales explícitas del README, plantillas de entorno, CORS fijo, readiness falso, endpoint de notificaciones, revocación por `token_version`, desafío MFA temporal, RBAC persistido, contrato de roles, placeholder de W01, scheduler duplicado y serialización de auditoría. Estas correcciones tienen validación estática; los estados de esta sección no se marcan como `COMPLETO` cuando requieren PostgreSQL, npm o una instancia n8n que no estaban disponibles en el entorno de trabajo. El detalle está en [`docs/CHANGELOG_CIERRE_P0.md`](./CHANGELOG_CIERRE_P0.md).

## Actualización de validación de ejecución — 2026-11-04

La validación ejecutable se documenta en [`docs/VALIDACION_P0.md`](./VALIDACION_P0.md). Se instaló `backend/.venv` y las dependencias declaradas, pero el Docker daemon no estaba disponible; por ello PostgreSQL/Redis, Alembic, endpoints HTTP y la integración completa de pytest quedaron `REQUIERE VALIDACIÓN MANUAL`. La única cabeza Alembic se comprobó con `0002 (head)`. n8n pasó validación estática de sus 30 JSON y referencias internas; su ejecución continúa pendiente de credenciales. Node 22.22.1 existe, npm no, por lo que frontend también requiere validación manual.

Los estados de la matriz original no se elevan a `COMPLETO` por esta ejecución. Ruff terminó con 69 hallazgos y mypy con 23 errores; no se hizo una refactorización masiva fuera del alcance P0.

## Correcciones derivadas de ejecución real — 2026-11-05

La infraestructura de pruebas quedó disponible y se ejecutó la validación completa. PostgreSQL/Redis healthy, Alembic aplicó `0001 -> 0002 -> 0003` y `current` coincide con la única cabeza `0003`. Backend terminó con 17 pruebas exitosas. `/health` respondió 200; `/ready` respondió 200 con dependencias y 503 al detener Redis.

Se corrigieron la IP simbólica de TestClient para PostgreSQL `INET`, el rollback de sesiones de pruebas, la canonicalización de la cadena hash y los tres fallos frontend: Flat Config ESLint 9, `ResizeObserver` en jsdom y validación explícita del login. Frontend quedó con typecheck, ESLint, Vitest y build en PASS.

Ruff global conserva 68 hallazgos de deuda técnica; Mypy conserva 23 errores relacionados con referencias/tipos opcionales y stubs externos. npm audit conserva 15 vulnerabilidades; las soluciones propuestas requieren actualizaciones mayores, por lo que no se ejecutó `--force`. P0 no se marca completamente validado mientras esos resultados de calidad/seguridad permanezcan pendientes.

| Área actualizada | Estado tras cambios | Motivo |
|---|---|---|
| Credenciales/documentación | REQUIERE VALIDACIÓN | La contraseña salió del README, pero la rotación histórica es manual |
| Variables de entorno | REQUIERE VALIDACIÓN | Se crearon ejemplos y documentación; falta probar arranque limpio |
| CORS | REQUIERE VALIDACIÓN | Código corregido y test añadido; pytest no puede ejecutarse sin dependencias |
| `/ready` | REQUIERE VALIDACIÓN | Código comprueba PostgreSQL/Redis; falta probar dependencias arriba/abajo |
| Notificaciones | REQUIERE VALIDACIÓN | Router y contrato frontend creados; falta PostgreSQL/HTTP integration test |
| Logout/revocación | PARCIAL | `token_version` implementado; falta prueba HTTP de refresh revocado |
| MFA | REQUIERE VALIDACIÓN | Desafío hash/expiración implementado y tests añadidos; falta ejecutar |
| RBAC/roles | REQUIERE VALIDACIÓN | Migración/API/frontend creados; falta aplicar Alembic y validar por rol |
| W01 HIBP | REQUIERE VALIDACIÓN | Placeholder eliminado y JSON válido; falta smoke test n8n con credenciales |
| Scheduler/orquestación | PARCIAL | Recolección backend desactivada por defecto; W02/W03 aún requieren validación de coordinación |
| Auditoría concurrente | REQUIERE VALIDACIÓN | Advisory lock añadido; requiere PostgreSQL y prueba concurrente |
| Tests | REQUIERE VALIDACIÓN | Falta `fastapi`; frontend carece de `npm` |

## Veredicto ejecutivo

El repositorio contiene una base amplia de backend, frontend, migración PostgreSQL y 15 workflows n8n, pero no existe evidencia suficiente para declarar una cadena operativa completa. La documentación describe varios componentes como entregados, aunque el código y la configuración muestran integraciones incompletas, endpoints faltantes, workflows inactivos y validación no ejecutada.

Estados usados: `COMPLETO` significa implementado y con evidencia razonable en código; `PARCIAL` significa que existe una parte pero faltan integración, cobertura o garantías; `FALTANTE` significa que no se encontró; `REQUIERE VALIDACIÓN` significa que el código existe, pero no pudo demostrarse en ejecución.

## Matriz de brechas

| Requisito | Implementación encontrada | Estado | Evidencia | Acción necesaria |
|---|---|---|---|---|
| Backend FastAPI | App, routers, servicios, health y métricas presentes; no se pudo arrancar por dependencias ausentes | REQUIERE VALIDACIÓN | [`backend/app/main.py`](../backend/app/main.py) | Instalar dependencias, levantar con PostgreSQL/Redis y ejecutar smoke tests de endpoints |
| Frontend React | Rutas, páginas, componentes, hooks y build configurados; no se ejecutaron `npm`/build | REQUIERE VALIDACIÓN | [`frontend/src/App.tsx`](../frontend/src/App.tsx), [`frontend/package.json`](../frontend/package.json) | Instalar Node/npm y ejecutar typecheck, lint, tests y build |
| PostgreSQL y Alembic | Migración inicial crea tablas, enums, extensiones, seeds y triggers; no se aplicó contra una instancia real | REQUIERE VALIDACIÓN | [`backend/alembic/versions/0001_initial.py`](../backend/alembic/versions/0001_initial.py) | Ejecutar `alembic upgrade head`, inspeccionar schema y probar rollback/restauración |
| Autenticación | Login, refresh JWT, MFA TOTP y `/me`; no hay revocación de refresh tokens ni endpoint de logout | PARCIAL | [`backend/app/api/v1/auth.py`](../backend/app/api/v1/auth.py), [`backend/app/core/security.py`](../backend/app/core/security.py) | Añadir estrategia de revocación/rotación persistente, logout y pruebas de expiración/replay |
| RBAC | Matriz backend y CASL frontend; `has_permission` usa solo matriz en memoria y no permisos cargados desde BD | PARCIAL | [`backend/app/core/rbac.py`](../backend/app/core/rbac.py), [`frontend/src/lib/abilities.ts`](../frontend/src/lib/abilities.ts) | Hacer consistente la fuente de permisos y probar cada rol contra cada endpoint |
| Usuarios, roles y perfiles | CRUD básico de usuarios y pantalla estática de roles; no hay API de roles ni protección fina de autoedición | PARCIAL | [`backend/app/api/v1/users.py`](../backend/app/api/v1/users.py), [`frontend/src/pages/Roles.tsx`](../frontend/src/pages/Roles.tsx) | Implementar/validar gestión de roles, perfil y límites de modificación |
| HIBP | Cliente con API key, caché Redis, rate limit y retries; ejecución principal también está en n8n y no se validó | PARCIAL | [`backend/app/services/hibp_client.py`](../backend/app/services/hibp_client.py) | Probar 200/404/429/5xx, caché y contrato de `breacheddomain` con plan HIBP real o fixture |
| Correlación de filtraciones | Cruce de usuarios activos, catálogo, severidad y hash deduplicado en backend/n8n | PARCIAL | [`backend/app/services/correlation.py`](../backend/app/services/correlation.py), [`n8n/workflows/W02_correlate.json`](../n8n/workflows/W02_correlate.json) | Validar payloads HIBP, dominios, usuarios sin match, duplicados y concurrencia |
| Contención | Reset de contraseña + revocación de sesiones, multi-IdP y persistencia de resultado | PARCIAL | [`backend/app/services/containment.py`](../backend/app/services/containment.py), [`backend/app/services/idp_client.py`](../backend/app/services/idp_client.py) | Probar cada IdP, fallos parciales, idempotencia y no exponer datos sensibles |
| Invalidación de sesiones | `revoke_sessions` existe en adaptadores Entra/webhook/LDAP; no hay invalidación local de JWT ya emitidos | PARCIAL | [`backend/app/services/idp_client.py`](../backend/app/services/idp_client.py) | Añadir `token_version`/denylist o TTL verificable y probar sesiones existentes |
| Notificaciones | Servicio SMTP/chat, modelo y router `/notifications` paginado; n8n W15 registra envíos | REQUIERE VALIDACIÓN | [`backend/app/services/notifications.py`](../backend/app/services/notifications.py), [`backend/app/api/v1/notifications.py`](../backend/app/api/v1/notifications.py), [`frontend/src/pages/Notifications.tsx`](../frontend/src/pages/Notifications.tsx) | Probar alcance por usuario/rol, PostgreSQL y SMTP/Teams con sandbox |
| Dashboard | KPIs, resumen, gráficos y consultas presentes | REQUIERE VALIDACIÓN | [`backend/app/api/v1/dashboard.py`](../backend/app/api/v1/dashboard.py), [`frontend/src/pages/Dashboard.tsx`](../frontend/src/pages/Dashboard.tsx) | Validar consultas PostgreSQL, zona horaria, datos vacíos y permisos |
| Reportes PDF/DOCX/XLSX | Generador y descarga con ReportLab, python-docx y openpyxl | REQUIERE VALIDACIÓN | [`backend/app/services/reporting.py`](../backend/app/services/reporting.py), [`backend/app/api/v1/reports.py`](../backend/app/api/v1/reports.py) | Generar cada combinación, validar hash/almacenamiento, permisos y descarga segura |
| Auditoría inmutable | Cadena de hash, triggers PostgreSQL, API de lectura/verificación y exportador | PARCIAL | [`backend/app/services/audit.py`](../backend/app/services/audit.py), [`backend/alembic/versions/0001_initial.py`](../backend/alembic/versions/0001_initial.py) | Probar concurrencia, alteración/borrado, continuidad de hash y exportación firmada |
| n8n y 15 workflows | Los 15 JSON canónicos están importados en n8n 2.46.6, con aliases y credenciales remapeados a IDs de instancia; todos permanecen desactivados | PARCIAL | [`n8n/workflows/`](../n8n/workflows), [`n8n/scripts/remap_workflow_ids.py`](../n8n/scripts/remap_workflow_ids.py), [`docs/N8N_VALIDACION.md`](./N8N_VALIDACION.md) | Ejecutar smoke tests controlados; HIBP/SMTP/Teams/IdP continúan sin integración real |
| Manejo de errores | Exception handler FastAPI, retries HIBP, DLQ n8n y W12 | PARCIAL | [`backend/app/main.py`](../backend/app/main.py), [`n8n/workflows/W12_error_handler.json`](../n8n/workflows/W12_error_handler.json) | Validar que no se pierdan errores, correlacionar execution IDs y definir alertas/retención |
| Variables de entorno | Backend y n8n ya tienen `.env.example`; frontend conserva su plantilla | REQUIERE VALIDACIÓN | [`backend/.env.example`](../backend/.env.example), [`n8n/.env.example`](../n8n/.env.example), [`docs/CONFIGURACION.md`](./CONFIGURACION.md) | Probar arranque limpio y verificar que no se copien placeholders a producción |
| Tests backend | 5 archivos/suites base; no se ejecutan en el entorno actual y el default SQLite no representa tipos PostgreSQL | REQUIERE VALIDACIÓN | [`backend/app/tests/`](../backend/app/tests), [`backend/app/tests/conftest.py`](../backend/app/tests/conftest.py) | Instalar dependencias, usar PostgreSQL de test o adaptar fixtures, añadir cobertura de integración |
| Tests frontend | 3 suites unitarias con mocks; no se ejecutaron | REQUIERE VALIDACIÓN | [`frontend/src/tests/`](../frontend/src/tests) | Ejecutar Vitest, revisar mocks, añadir rutas protegidas, errores, reportes y notificaciones |
| Docker | Dockerfiles backend/frontend; dos Compose incompatibles en alcance y n8n `latest` sin pin | PARCIAL | [`backend/docker-compose.yml`](../backend/docker-compose.yml), [`n8n/docker-compose.n8n.yml`](../n8n/docker-compose.n8n.yml) | Definir stack único reproducible, fijar versiones, healthchecks reales, red/proxy y secretos |
| Documentación | README y tres especificaciones extensas; existen discrepancias con código y falta guía operativa segura | PARCIAL | [`README.md`](../README.md), [`SPEC_BACKEND.md`](../SPEC_BACKEND.md), [`SPEC_FRONTEND.md`](../SPEC_FRONTEND.md), [`SPEC_N8N.md`](../SPEC_N8N.md) | Actualizar documentación con estado verificado, prerequisitos, variables y procedimientos de operación |
| Seguridad | SecretStr, HMAC, hash de auditoría, headers Nginx, CORS configurable, revocación por versión y MFA con desafío temporal | PARCIAL | [`README.md`](../README.md), [`frontend/nginx.conf`](../frontend/nginx.conf), [`backend/app/core/config.py`](../backend/app/core/config.py), [`backend/app/api/v1/auth.py`](../backend/app/api/v1/auth.py) | Rotar manualmente la contraseña histórica, validar TLS/rate limiting y ejecutar pruebas de auth |
| Calidad del código | Separación por capas y tipado razonable; duplicación `tmp_import`, código no conectado y validación local bloqueada | PARCIAL | [`n8n/workflows/tmp_import/`](../n8n/workflows/tmp_import), [`backend/app/services/`](../backend/app/services) | Eliminar duplicación solo tras confirmar uso, añadir lint/mypy y corregir contratos backend/frontend |
| Experimentos/resultados científicos | No se encontraron experimentos reproducibles ni resultados instrumentados en el repositorio | FALTANTE | [`README.md`](../README.md) | Crear protocolo, fixtures, métricas y resultados reproducibles; no inventar valores |

## Discrepancias entre especificaciones y código

- [`SPEC_BACKEND.md`](../SPEC_BACKEND.md) concluye que los 24 módulos están implementados y declara 5 suites base. El cierre P0 añadió `/notifications` y trasladó la autorización a permisos persistidos; la prueba real quedó bloqueada por `ModuleNotFoundError: fastapi`.
- [`SPEC_FRONTEND.md`](../SPEC_FRONTEND.md) presenta CI, tests y 24 módulos como entregados, pero el CI está bajo [`frontend/.github/workflows/ci.yml`](../frontend/.github/workflows/ci.yml), no hay pipeline raíz que valide backend/n8n, y en el entorno auditado `npm` no está disponible. La pantalla de notificaciones llama a una ruta ausente.
- [`SPEC_N8N.md`](../SPEC_N8N.md) afirma 15 workflows completos, 92 nodos y smoke tests, pero los JSON están inactivos y no incluyen las credenciales operativas. El placeholder de W01 fue eliminado en los JSON principales y en `tmp_import`; la copia paralela sigue requiriendo una fuente canónica documentada.
- [`README.md`](../README.md) indica un PostgreSQL existente en puerto 5433 y arranque n8n separado, mientras [`backend/docker-compose.yml`](../backend/docker-compose.yml) define PostgreSQL, Redis, API y n8n en otra topología/puertos. Falta una ruta de reproducción única.

## Workflows n8n: revisión específica

La fuente canónica `n8n/workflows/` contiene 15 JSON válidos W01–W15. La instancia `n8nio/n8n:2.46.6` registró los 15 mediante una copia temporal sin el metadato `tags`, porque la importación directa falló con `workflows_tags.tagId` al recibir tags como strings. Los 15 quedaron desactivados; no se activó ningún cron, webhook ni error handler. El detalle de inventario y validación está en [`docs/N8N_VALIDACION.md`](./N8N_VALIDACION.md).

Hallazgos operacionales actuales:

1. `Radar PG` está configurada y probó conexión exitosamente; `Radar SMTP` existe como sandbox sin listener local; `HIBP API` requiere una clave autorizada o fixture.
2. Las conexiones entre nodos son sintácticamente válidas y el remapeo autenticado de la instancia ya fue aplicado. El script también resuelve credenciales portables y usa el endpoint de desactivación n8n 2.x.
3. W01 persiste en `hibp_cache`, mientras FastAPI administra caché HIBP mediante Redis; queda una duplicación arquitectónica pendiente.
4. W03/W04 realizan llamadas IdP desde n8n y FastAPI también implementa contención; no se ejecutaron resets reales y la responsabilidad debe alinearse con ADR-001.
5. W09 delega generación/descarga de reportes en FastAPI; requiere credencial/autorización HTTP o sandbox antes de ejecución.
6. W13 ahora delega el registro en `/api/v1/audit/internal`, que valida `RADAR_SERVICE_TOKEN` y llama a `write_audit`; W07 delega `/api/v1/audit/verify`. La ruta backend fue probada con TestClient y la cadena operacional quedó íntegra; ninguno fue ejecutado desde n8n.
7. La CLI `n8n execute` no pudo iniciar por conflicto del task broker en el puerto `5679`; por ello no hay execution IDs ni smoke test E2E. Los 15 workflows siguen desactivados.

## Secretos y reproducibilidad

- No se encontraron archivos `.env` versionados ni claves privadas. Sí se encontró una contraseña operativa explícita en [`README.md`](../README.md), líneas 68–69; debe eliminarse del historial/documentación y rotarse si fue usada.
- [`frontend/.env.example`](../frontend/.env.example) solo cubre tres variables del frontend. No es suficiente para reproducir backend ni n8n: faltan `DATABASE_URL`, `JWT_SECRET`, `HIBP_API_KEY`, Redis, IdP, SMTP, webhooks, usuario/contraseña n8n y demás variables referenciadas.
- Las credenciales n8n no están versionadas, lo cual es correcto desde seguridad, pero debe existir un procedimiento seguro de creación/asignación y una validación automatizada que detecte referencias sin credencial.

## Errores evidentes de integración

- React solicita `GET /api/v1/notifications`, pero FastAPI no registra router de notificaciones.
- `frontend/nginx.conf` proxyfica `/api/` hacia `api:8000`, pero el Compose n8n separado no define ese servicio y el README propone frontend/Vite nativo; la topología depende de dónde se ejecute el frontend.
- El backend usa `CORS_ORIGINS` configurable, pero [`backend/app/main.py`](../backend/app/main.py) ignora esa configuración y fija dos orígenes.
- La autenticación MFA devuelve token vacío en el primer login y depende de que el frontend redirija correctamente; no hay estado de desafío persistente ni expiración del desafío.
- El frontend persiste access y refresh tokens en `localStorage`, aumentando impacto de XSS.
- El endpoint `/ready` siempre devuelve `ready` aunque no comprueba DB ni Redis, contradiciendo su propósito operativo.
- Los tests default usan SQLite aunque los modelos/migración usan `CITEXT`, `ARRAY`, `JSONB`, `INET`, enums y triggers PostgreSQL.
- Los JSON canónicos ya no contienen el placeholder de catálogo W01 ni la consulta `WHERE FALSE`; n8n y backend todavía duplican parte de la lógica de correlación, contención y notificación, pendiente de validación operacional.

## Código muerto, placeholders y mocks

- El catálogo falso de W01 fue eliminado; la consulta oficial queda en W02 y requiere credencial/sandbox HIBP.
- [`n8n/workflows/tmp_import/`](../n8n/workflows/tmp_import/) duplica los 15 workflows con contenido distinto; la fuente canónica usada fue [`n8n/workflows/`](../n8n/workflows/), y `tmp_import` no fue importado.
- La importación directa de tags es incompatible con n8n 2.46.6; se usó una copia temporal sin tags y se registró el incidente en [`docs/N8N_VALIDACION.md`](./N8N_VALIDACION.md).
- Las pruebas frontend mockean hooks y solo cubren renderizado/validación básica; no prueban integración HTTP, permisos ni errores.
- La pantalla de roles usa una matriz constante; no es CRUD de roles ni refleja necesariamente permisos de BD.
- El servicio de scheduler y notificaciones existe, pero su ejecución real y el flujo completo desde scheduler hasta persistencia no fueron demostrados.

## Plan de cierre priorizado

### P0 — bloquear riesgo y falsas garantías

1. Retirar la contraseña de administrador de [`README.md`](../README.md), rotarla y revisar historial/secret scanning.
2. Crear `.env.example` seguros para backend y n8n, sin valores operativos; documentar cómo generar secretos.
3. Elegir el orquestador principal (n8n o backend) para evitar doble contención/notificación/auditoría.
4. Eliminar el placeholder de catálogo HIBP y probar W01–W03 con fixtures controladas.
5. Corregir la ruta `/notifications` o retirar temporalmente la pantalla hasta tener contrato backend.

### P1 — hacer reproducible el sistema

1. Levantar PostgreSQL/Redis y aplicar Alembic en un entorno limpio.
2. Ejecutar backend tests contra PostgreSQL de prueba; añadir cobertura de auth, RBAC, HIBP, contención, auditoría y reportes.
3. Instalar dependencias frontend y ejecutar typecheck, lint, Vitest y build.
4. Importar n8n en una instancia efímera, asignar credenciales de prueba, activar por etapas y ejecutar smoke tests de los 15 workflows.
5. Unificar Compose/README, fijar `n8nio/n8n` a versión, añadir healthchecks reales y definir red/API/proxy.

### P2 — endurecimiento y calidad

1. Implementar revocación local de tokens, logout, desafío MFA con expiración y almacenamiento seguro distinto de `localStorage` si el modelo lo permite.
2. Hacer que backend use `settings.CORS_ORIGINS`, añadir rate limiting HTTP, TLS/headers CSP compatibles con API y controles de proxy.
3. Serializar escritura de la cadena de auditoría y probar alteración, borrado, concurrencia y exportación.
4. Sustituir roles estáticos por contrato respaldado por API/BD y aplicar autorización de perfil.
5. Definir fixtures, protocolo de medición y resultados científicos reproducibles.

## Archivos creados por esta auditoría

- [`AGENTS.md`](../AGENTS.md)
- [`docs/GAP_ANALYSIS.md`](./GAP_ANALYSIS.md)

No se modificaron implementaciones funcionales ni se realizó refactorización masiva.

## Comandos pendientes de ejecución

```bash
# Backend
cd backend
python -m pip install -e ".[dev]"
alembic upgrade head
pytest -q
ruff check app
mypy app

# Frontend
cd ../frontend
npm ci
npm run typecheck
npm run lint
npm test -- --run
npm run build

# Docker / n8n
cd ..
docker compose -f backend/docker-compose.yml config
docker compose -f backend/docker-compose.yml up --build
docker compose -f n8n/docker-compose.n8n.yml config
# Importar/asignar credenciales en una instancia n8n de prueba y ejecutar smoke tests W01–W15
```
## Actualización de smoke test n8n

La evidencia de ejecución real está en [N8N_SMOKE_E2E.md](./N8N_SMOKE_E2E.md). Se validaron W14, W13, W07, W10 y W15 localmente. El E2E W01→W02→W03 sigue pendiente: W01 finaliza sin filas desde la conexión PostgreSQL de n8n y, por consecuencia, no existe todavía un `leak_hit`/`reset` fixture. No se marca el P0 operacional como completamente validado.

La causa técnica comprobada es la contraseña no persistida/incorrecta en la credencial n8n: la conexión directa desde el contenedor al mismo host, puerto y base sí devuelve datos, mientras el nodo PostgreSQL falla en autenticación. No se marcaron W01–W03 como funcionales.

### Corrección y ejecución posterior

La actualización del 2026-11-05 queda documentada en [N8N_SMOKE_E2E.md](./N8N_SMOKE_E2E.md). La credencial antigua estaba asociada al propietario anterior de n8n y no conservaba un secreto utilizable; se creó la credencial del propietario actual contra `radar_creds` y se rebindearon los nodos PostgreSQL. Después, W01→W02→W03 completó una ejecución real con fixtures (IDs 89, 90 y 92), creando un `leak_hit`, un `reset`, notificaciones y auditoría. W07 terminó correctamente con ID 96 y `/audit/verify` devolvió `ok=true`, `broken=[]`.

Correcciones de integración derivadas de ejecución: sincronización de entradas W02, recuperación del UUID insertado, sincronización de respuestas paralelas de W03, serialización de `entidad_id` en W01 y lectura JSON directa en W07. W04, W05, W06, W08, W09, W11 y W12 aún requieren ejecución individual con fixtures; no se declaran completos.

### Cierre de pendientes n8n

La ejecución del 2026-11-05 cerró los pendientes operacionales: W04 (reintento, recuperación y límite), W05, W06, W08 (HMAC válido/inválido), W09 (PDF), W11 (health 200/500) y W12 (Error Trigger) quedaron documentados como PASS CON FIXTURE en [N8N_SMOKE_E2E.md](./N8N_SMOKE_E2E.md). W02 NO MATCH quedó validado con el execution ID 98 y sin registros secundarios. Los IDs reales finales son leak `0d9bb95f-a669-4577-b5ca-a61d08908b76`, reset `f62e1063-9b57-40f8-b0a7-163a66566091` y notificación asociada `01598bed-4762-4a62-b927-eaad31b5ed1b`.

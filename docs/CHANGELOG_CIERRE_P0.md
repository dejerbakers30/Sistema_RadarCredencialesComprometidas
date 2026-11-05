# Changelog de cierre P0

Fecha: 2026-11-04

Se modificó el repositorio existente sin reconstruir módulos ni alterar el historial Git.

| Problema | Archivo afectado | Solución | Pruebas | Estado |
|---|---|---|---|---|
| Credencial administrativa explícita | [`README.md`](../README.md) | Sustituida por placeholder seguro y nota de rotación manual | Búsqueda estática sin contraseña histórica | Validado estáticamente; rotación manual pendiente |
| `.env` y credenciales n8n sin política suficiente | [`.gitignore`](../.gitignore), [`backend/.env.example`](../backend/.env.example), [`n8n/.env.example`](../n8n/.env.example) | Se excluyeron `.env.*`/credenciales y se añadieron plantillas seguras | Revisión de variables y `git check-ignore` | Validado estáticamente |
| Configuración no reproducible | [`docs/CONFIGURACION.md`](./CONFIGURACION.md) | Variables clasificadas como REQUERIDA/OPCIONAL/SOLO DESARROLLO/SOLO PRODUCCIÓN | Revisión estática | Requiere validación de arranque |
| CORS fijo | [`backend/app/main.py`](../backend/app/main.py) | Usa exclusivamente `settings.CORS_ORIGINS` | Test añadido; no ejecutable sin FastAPI | Requiere validación |
| `/ready` falso | [`backend/app/main.py`](../backend/app/main.py) | Comprueba PostgreSQL y Redis requerido y responde 503 sin secretos | Test de error añadido; requiere servicios | Requiere validación |
| Notificaciones sin endpoint | [`backend/app/api/v1/notifications.py`](../backend/app/api/v1/notifications.py), [`frontend/src/pages/Notifications.tsx`](../frontend/src/pages/Notifications.tsx) | Listado paginado, filtros y alcance por usuario/roles administrativos | Contrato compilable; integración pendiente | Requiere validación |
| Logout y revocación ausentes | [`backend/app/api/v1/auth.py`](../backend/app/api/v1/auth.py), [`backend/app/core/security.py`](../backend/app/core/security.py) | `token_version`, endpoint logout y comprobación en access/refresh | Test de claim; HTTP integration pendiente | Parcial |
| MFA sin desafío temporal | [`backend/app/api/v1/auth.py`](../backend/app/api/v1/auth.py), [`backend/app/core/security.py`](../backend/app/core/security.py) | Hash persistido, expiración configurable y TOTP descifrado solo en verificación | Tests válido/incorrecto/expirado añadidos | Requiere validación |
| RBAC duplicado | [`backend/app/core/rbac.py`](../backend/app/core/rbac.py), [`backend/app/api/deps.py`](../backend/app/api/deps.py), [`backend/alembic/versions/0002_security_rbac.py`](../backend/alembic/versions/0002_security_rbac.py) | BD como fuente de verdad, permisos sembrados por migración y API de roles | Compilación; migración pendiente | Requiere validación PostgreSQL |
| Roles frontend estáticos | [`backend/app/api/v1/roles.py`](../backend/app/api/v1/roles.py), [`frontend/src/hooks/useRoles.ts`](../frontend/src/hooks/useRoles.ts), [`frontend/src/pages/Roles.tsx`](../frontend/src/pages/Roles.tsx) | Consulta real de roles, permisos y usuarios | Compilación sintáctica; build pendiente | Requiere validación |
| Placeholder HIBP de W01 | [`n8n/workflows/W01_collect.json`](../n8n/workflows/W01_collect.json), [`SPEC_N8N.md`](../SPEC_N8N.md) | Eliminado; catálogo oficial se consulta en W02 mediante `/breaches` | Todos los JSON parsean; smoke test n8n pendiente | Requiere validación manual |
| Scheduler duplicado | [`backend/app/services/scheduler.py`](../backend/app/services/scheduler.py), [`backend/app/core/config.py`](../backend/app/core/config.py), [`docs/ADR-001-ORQUESTACION.md`](./ADR-001-ORQUESTACION.md) | Recolección backend desactivada por defecto; n8n coordina el proceso diario | Revisión estática | Requiere validación de despliegue |
| Cadena de auditoría concurrente | [`backend/app/services/audit.py`](../backend/app/services/audit.py), [`backend/alembic/versions/0002_security_rbac.py`](../backend/alembic/versions/0002_security_rbac.py) | Advisory lock transaccional en servicio y trigger; UPDATE/DELETE permanecen bloqueados | Test concurrente y de inmutabilidad añadidos | Requiere PostgreSQL |
| SQLite usado para integración | [`backend/app/tests/conftest.py`](../backend/app/tests/conftest.py), [`backend/docker-compose.test.yml`](../backend/docker-compose.test.yml) | Integración requiere PostgreSQL aislado | Compose de test validado; ejecución pendiente | Requiere validación |

## Validaciones ejecutadas

- `python3 -m compileall -q backend/app backend/alembic`: exitoso.
- Parseo de todos los JSON de `n8n/workflows/` y `tmp_import/`: exitoso.
- `git diff --check`: exitoso tras corregir formato.
- `POSTGRES_TEST_PASSWORD=not-real docker compose -f backend/docker-compose.test.yml config`: exitoso.
- `python3 -m pytest -q`: falló antes de recolectar por `ModuleNotFoundError: fastapi`.
- `npm run typecheck`: no ejecutado; el entorno no tiene `npm`.
- Compose n8n: requiere copiar `n8n/.env.example` a `n8n/.env`; no se creó ese archivo para evitar secretos/configuración local en el repositorio.

## Pendientes manuales

1. Rotar la contraseña histórica si fue utilizada.
2. Instalar dependencias en un entorno controlado.
3. Levantar PostgreSQL de test con `POSTGRES_TEST_PASSWORD` fuera de Git y aplicar Alembic.
4. Ejecutar pytest backend, incluyendo auth, MFA, RBAC, notificaciones y concurrencia.
5. Ejecutar typecheck, lint, Vitest y build frontend.
6. Configurar credenciales n8n en una instancia efímera y ejecutar smoke tests W01–W15.
7. Validar manualmente que el scheduler de recolección FastAPI permanezca desactivado cuando n8n esté activo.

## Validación de ejecución — 2026-11-04

Se creó [`docs/VALIDACION_P0.md`](./VALIDACION_P0.md). El entorno virtual se instaló correctamente y las importaciones principales pasaron. La validación de integración quedó bloqueada porque el Docker daemon no está disponible; por tanto, no se aplicaron migraciones ni se usó una base alternativa. Node está disponible, pero npm no está instalado. La validación estática de n8n pasó para 30 JSON, sin referencias rotas ni placeholders.

Se añadió Redis al Compose aislado de pruebas [`backend/docker-compose.test.yml`](../backend/docker-compose.test.yml), necesario para validar `/ready` con la dependencia configurada, sin modificar los Compose de desarrollo o producción.

Resultados exactos, comandos y estados: [`docs/VALIDACION_P0.md`](./VALIDACION_P0.md).

## Reintento de validación — 2026-11-04

Se reintentó la ejecución con `docker compose -f backend/docker-compose.test.yml ps`, `pytest -q`, Ruff, Mypy y la validación estática n8n. En la sesión actual el contexto Docker sigue apuntando a `/var/run/docker.sock`, cuyo socket no existe, y `npm` no está instalado. Por ello los componentes de infraestructura, Alembic, readiness y frontend permanecen `REQUIERE VALIDACIÓN MANUAL`; no se utilizó otra base de datos ni se simularon resultados.

## Correcciones derivadas de ejecución real — 2026-11-05

La ejecución posterior se realizó con PostgreSQL 16 y Redis 7 healthy. Se corrigió la normalización de IP para `INET`, el rollback de la fixture, la canonicalización única de hashes de auditoría mediante la migración `0003`, la configuración Flat Config de ESLint 9, el mock global de `ResizeObserver` y la validación accesible del login.

Resultado: backend `17 passed`; Alembic `0003 (head)` con una única cabeza; `/health` HTTP 200; `/ready` HTTP 200 con dependencias y HTTP 503 al detener Redis; frontend typecheck, lint, Vitest y build PASS. Ruff global mantiene 68 hallazgos y Mypy 23 errores/stubs. npm audit mantiene 15 vulnerabilidades y no se ejecutó `--force`.

La matriz detallada de causa, corrección y prueba está en [`docs/VALIDACION_P0.md`](./VALIDACION_P0.md).
# Validación smoke n8n — 2026-11-05

- Se ejecutaron workflows mediante la API local de n8n y se conservaron execution IDs reales: W14 `12,13`, W13 `15`, W07 `17`, W15 `21,22`, W10 `25`, W01 `27,29`, W02 `28`, W05 `23`, W08 `24` y W11 `26`.
- W14, W13 y W07 fueron PASS; W15 y W10 fueron PASS CON FIXTURE. Mailpit aceptó el correo sintético y el receptor Teams local guardó evidencia.
- W01/W02 no completaron correlación: W01 terminó sin filas de dominios desde la conexión PostgreSQL de n8n y W02 se detuvo en `Merge & Enrich`. No se declaró `leak_hit`, `reset` ni E2E completo.
- La suite backend se ejecutó contra `radar_test`: `19 passed`.
- Frontend: typecheck PASS, ESLint PASS con seis warnings, Vitest `9 passed`, build PASS.
- Detalle reproducible: [N8N_SMOKE_E2E.md](./N8N_SMOKE_E2E.md).

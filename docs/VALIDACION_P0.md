# Validación de cierre P0

Fecha de ejecución: 2026-11-04  
Entorno: Linux, Python 3.14.4, repositorio actual. No se usó la base de desarrollo ni una base productiva.

## Matriz de ejecución

| Componente | Prueba ejecutada | Resultado | Evidencia |
|---|---|---|---|
| Entorno Python | `python3 -m venv backend/.venv` e instalación `pip install -e ".[dev]"` | PASS | Instalación editable finalizada; importaciones verificadas |
| Dependencias backend | Importación de FastAPI, SQLAlchemy, Alembic y pytest | PASS | FastAPI 0.162.0; SQLAlchemy 2.1.8; Alembic 1.20.1; pytest 9.2.0 |
| PostgreSQL/Redis de test | `docker compose -f backend/docker-compose.test.yml up -d` | REQUIERE VALIDACIÓN MANUAL | Docker CLI existe, pero no hay daemon en `/var/run/docker.sock` en esta sesión |
| Alembic upgrade | `alembic upgrade head` contra `127.0.0.1:55432/radar_test` | REQUIERE VALIDACIÓN MANUAL | No había PostgreSQL de test escuchando; no se ejecutó contra otra base |
| Alembic heads | `alembic heads` | PASS | Única cabeza reportada: `0002 (head)` |
| Backend pytest | `pytest -q` con `TEST_DATABASE_URL` de test | REQUIERE VALIDACIÓN MANUAL | 5 passed; 6 errores de setup por conexión PostgreSQL no disponible |
| Ruff | `ruff check app` | FAIL | 69 hallazgos de lint/estilo en el árbol actual |
| Mypy | `mypy app` | FAIL | 23 errores de tipado/stubs; no se modificó tipado masivamente |
| Health/readiness HTTP | Arranque de FastAPI y `/health`, `/ready` con DB/Redis | REQUIERE VALIDACIÓN MANUAL | Requiere PostgreSQL/Redis de test y no se pudo levantar el stack |
| Frontend runtime | `node --version`, `npm --version` | REQUIERE VALIDACIÓN MANUAL | Node 22.22.1 disponible; `npm` no está instalado |
| Frontend typecheck/lint/tests/build | `npm ci`, `npm run typecheck`, `npm run lint`, `npm test -- --run`, `npm run build` | REQUIERE VALIDACIÓN MANUAL | No se ejecutó ningún comando npm por ausencia de npm |
| n8n JSON | Parseo de todos los JSON y referencias de conexiones | PASS | 30 JSON válidos; 0 referencias a nodos inexistentes |
| n8n placeholders | Búsqueda de `Placeholder Catalog` y `WHERE FALSE` | PASS | No se encontraron coincidencias en workflows ni especificación |
| n8n operacional | Smoke test W01–W15 con credenciales | REQUIERE VALIDACIÓN MANUAL | No existen credenciales n8n operativas en el repositorio |
| Secretos versionados | `git ls-files`, `git check-ignore` y revisión de patrones | PASS | `.env` real ignorado; `.env.example` versionable; no se detectaron PEM/credenciales versionados |

## Resumen cuantitativo

- Tests backend: 11 casos recolectados; 5 exitosos; 0 fallos de aserción; 6 errores de preparación por PostgreSQL no disponible.
- Migraciones aplicadas: ninguna en esta ejecución. La cabeza declarada por Alembic es única: `0002`.
- Ruff: FAIL, 69 hallazgos.
- Mypy: FAIL, 23 errores.
- Frontend: REQUIERE VALIDACIÓN MANUAL; Node está instalado, npm no.
- Build frontend: no ejecutado.
- n8n: validación estática PASS; validación operacional pendiente.

## Conclusión

El P0 no puede declararse completamente validado. La instalación Python y las comprobaciones estáticas son reproducibles, pero la evidencia esencial de PostgreSQL/Redis, migraciones, endpoints HTTP, autenticación, MFA, RBAC, notificaciones, auditoría concurrente y frontend requiere ejecutar el entorno con Docker daemon y npm disponibles.

## Tareas manuales pendientes

1. Iniciar Docker daemon y ejecutar únicamente `backend/docker-compose.test.yml` con `POSTGRES_TEST_PASSWORD` de prueba.
2. Ejecutar `alembic upgrade head`, `alembic current`, `alembic heads` y comprobar migración desde cero.
3. Repetir `pytest -q`, incluyendo los casos de auth, MFA, RBAC, notificaciones, readiness y auditoría concurrente.
4. Instalar npm compatible con Node 20+ y ejecutar typecheck, lint, Vitest y build.
5. Ejecutar smoke tests W01–W15 en una instancia n8n efímera con credenciales de prueba no productivas.
6. Resolver o aceptar explícitamente los 69 hallazgos de Ruff y 23 errores de Mypy antes del cierre técnico.
7. Rotar manualmente cualquier contraseña histórica que haya sido utilizada.

## Correcciones derivadas de ejecución real — 2026-11-05

| Problema | Causa raíz | Corrección | Prueba | Resultado |
|---|---|---|---|---|
| `testclient` no era válido para `audit_log.ip_origen` | `INET` recibía directamente el host simbólico de TestClient | Helper `normalize_ip` basado en `ipaddress`; no se confía en `X-Forwarded-For` | Casos IPv4, IPv6, IP externa, host simbólico, vacío y `None` | PASS |
| `PendingRollbackError` en teardown | Fixture hacía `commit()` después de una prueba con error de DB | Fixture termina con `rollback()` y cierra siempre la sesión | Suite PostgreSQL completa | PASS |
| Cadena de auditoría inválida | Trigger `0002` recalculaba un hash distinto al de Python | Migración `0003`; payload canónico único para escritura/verificación y advisory lock conservado | Cadena, inmutabilidad y concurrencia PostgreSQL | PASS |
| ESLint 9 incompatible | Solo existía configuración legacy `.eslintrc.cjs` | Flat Config en `eslint.config.js` | `npm run lint` | PASS; 8 warnings no bloqueantes |
| Dashboard fallaba por `ResizeObserver` | jsdom no implementa la API requerida por Recharts | Mock global reutilizable en setup de Vitest | `npm test -- --run` | PASS |
| Login no mostraba validación explícita | Validación nativa `type=email` impedía el flujo esperado en jsdom | Validación Zod accesible para email, contraseña y formulario válido | 3 pruebas de Login | PASS |

### Resultados actualizados

- PostgreSQL 16 y Redis 7: PASS; ambos healthy en `docker-compose.test.yml`.
- Alembic: PASS; `0001`, `0002` y `0003` aplicados; única cabeza y revisión actual `0003 (head)`.
- Backend: `17 passed`, `0 failed`, `0 errors`, `0 skipped`.
- `/health`: PASS, HTTP 200.
- `/ready` con DB/Redis: PASS, HTTP 200.
- `/ready` con Redis detenido: PASS, HTTP 503 sin exponer secretos.
- Frontend typecheck: PASS.
- ESLint 9: PASS con 8 warnings no bloqueantes.
- Vitest: 3 archivos y 5 tests PASS.
- Build producción: PASS; permanece únicamente warning de chunks mayores a 500 kB.
- Ruff global: FAIL, 68 hallazgos preexistentes/deuda técnica; los archivos corregidos de auditoría y fixture pasan Ruff.
- Mypy: FAIL, 23 errores de tipado/stubs no bloqueantes para esta corrección.
- npm audit: 15 vulnerabilidades antes y 15 después; `npm audit fix --dry-run` no encontró actualización compatible. Las correcciones disponibles requieren cambios mayores.

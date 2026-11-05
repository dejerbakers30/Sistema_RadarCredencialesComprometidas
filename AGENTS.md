# Guía de trabajo del repositorio

## Arquitectura

- `backend/`: API FastAPI, servicios de HIBP/IdP/notificaciones/reportes, modelos SQLAlchemy y migraciones Alembic.
- `frontend/`: aplicación React + Vite + TypeScript, TanStack Query, Zustand, CASL y Tailwind.
- `n8n/`: Compose y los 15 workflows JSON que orquestan recolección, correlación, contención, reintentos, auditoría y notificaciones.
- `infra/`: espacio reservado para infraestructura adicional.
- PostgreSQL es la base de datos de aplicación; Redis se usa para caché/soporte de reintentos en el backend.

## Comandos de backend

Desde `backend/`, con un entorno virtual activo:

```bash
python -m pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Crear el administrador inicial requiere parámetros explícitos; no deben fijarse credenciales en el código:

```bash
python -m app.cli create-admin --email <email> --password '<password>'
```

## Comandos de frontend

Desde `frontend/`:

```bash
npm ci
npm run dev
npm run typecheck
npm run lint
npm test -- --run
npm run build
```

## Tests y validación

```bash
cd backend && pytest -q
cd frontend && npm test -- --run
```

La ejecución debe hacerse con PostgreSQL/Redis y variables de entorno de prueba configuradas. No se debe presentar una ejecución no realizada como resultado. Antes de aceptar cambios, validar también `alembic upgrade head`, el arranque de FastAPI, el build frontend y una prueba de humo de cada workflow n8n.

## Docker

```bash
docker compose -f backend/docker-compose.yml up --build
docker compose -f n8n/docker-compose.n8n.yml up -d
```

El Compose de n8n requiere su propio `.env`; sus workflows requieren credenciales n8n configuradas en la instancia. No activar workflows en producción sin probarlos con datos controlados.

## Restricciones de seguridad

- No versionar `.env`, contraseñas, API keys, tokens, certificados privados ni credenciales exportadas.
- Rotar inmediatamente cualquier secreto que haya aparecido en Git o en documentación.
- Mantener secretos en el gestor de secretos/variables de entorno y usar valores de ejemplo no operativos en plantillas.
- No registrar contraseñas, tokens, secretos MFA ni respuestas sensibles del IdP en logs o auditoría.
- Verificar autorización en backend; el RBAC del frontend es solo una ayuda de interfaz.
- Validar firma HMAC, expiración de tokens, invalidación de sesiones, CORS y TLS antes de un despliegue real.

## Cambios y archivos sensibles

No modificar innecesariamente `backend/alembic/versions/`, `backend/app/core/security.py`, `backend/app/services/audit.py` ni los JSON de `n8n/workflows/`: cualquier cambio allí debe acompañarse de migración, pruebas y una prueba de integración. No borrar `n8n/workflows/tmp_import/` sin confirmar su propósito y actualizar la documentación de importación.

## Resultados experimentales

No inventar métricas, resultados científicos, porcentajes de cobertura ni resultados de pruebas. Registrar solo ejecuciones reproducibles, con fecha, comando, entorno y salida verificable. Si una prueba no puede ejecutarse, marcarla como bloqueada o requiere validación.

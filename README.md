# Radar de Credenciales Comprometidas

Radar de Credenciales Comprometidas es un SOC (Security Operations Center) automatizado que detecta filtraciones de correos corporativos mediante Have I Been Pwned (HIBP), orquesta la respuesta con n8n y almacena la información en PostgreSQL. El sistema permite gestionar la contención de credenciales expuestas y mantiene una bitácora inmutable con encadenamiento de hashes y protección contra modificaciones y borrados, que aporta evidencia para los controles de auditoría de ISO 27001.

## Stack tecnológico

| Componente | Tecnologías |
| --- | --- |
| Backend | Python, FastAPI, SQLAlchemy |
| Frontend | React, Vite, Tailwind CSS |
| Base de datos | PostgreSQL 16 |
| Automatización | n8n, con 15 workflows |
| Despliegue | Docker para PostgreSQL y n8n; Uvicorn y Vite ejecutados de forma nativa |

## Requisitos previos

- Python 3.12 o superior.
- Node.js 20 o superior y npm.
- Docker Desktop instalado y en ejecución.
- Dependencias del backend instaladas en `backend/.venv` y dependencias del frontend instaladas.
- Archivos `backend/.env` y `n8n/.env` configurados, migraciones aplicadas y workflows importados con sus credenciales asignadas.

## Instrucciones de arranque

Ejecuta los siguientes pasos desde la raíz del proyecto, utilizando una terminal distinta para cada servicio.

### Terminal 1: Docker

La base de datos local del proyecto se publica en el puerto `55433` para evitar conflictos con otros servicios PostgreSQL. Asegúrate de que esté iniciado en Docker antes de levantar n8n. El Compose de n8n no inicia PostgreSQL.

```powershell
docker compose -f n8n/docker-compose.n8n.yml up -d
```

n8n utiliza la base interna `n8n`, separada de la base de la aplicación `bd_sistemacredencialescompartidas`.

### Terminal 2: Backend

Activa el entorno virtual en Windows y deja Uvicorn ejecutándose:

```powershell
cd backend
.venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 3: Frontend

```powershell
cd frontend
npm run dev
```

### Direcciones de acceso

| Servicio | Dirección |
| --- | --- |
| Aplicación web | http://127.0.0.1:5173 |
| API | http://127.0.0.1:8000 |
| Documentación interactiva de la API | http://127.0.0.1:8000/docs |
| Estado del backend | http://127.0.0.1:8000/health |
| n8n | http://localhost:5678 |

## Configuración del administrador inicial

Crear el administrador mediante el comando seguro de [`AGENTS.md`](AGENTS.md), usando valores definidos fuera del repositorio:

- **Email de ejemplo:** `admin@example.com`
- **Contraseña:** `<CONFIGURAR_PASSWORD_ADMIN>`

La contraseña histórica que aparecía en versiones anteriores de esta documentación debe rotarse manualmente si fue utilizada. Este cambio no modifica el historial Git.

La cuenta Owner de n8n se configura por separado en su interfaz.

## Módulos del sistema

- **Dashboard:** muestra indicadores de exposición, filtraciones pendientes y contenidas, tiempo medio de contención, tendencias, severidad y reincidencias.
- **Filtraciones:** permite consultar y filtrar los correos detectados en breaches, revisar los datos expuestos y gestionar su estado y severidad.
- **Contenciones:** registra los restablecimientos de contraseña y la revocación de sesiones, permite solicitar contenciones manuales y consultar resultados y reintentos.
- **Reportes:** genera reportes operacionales en PDF, de gestión en Word y ejecutivos en Excel para su descarga.
- **Auditoría inmutable:** registra las acciones del sistema en una cadena de hashes. Los triggers de PostgreSQL impiden actualizar o eliminar registros, y la verificación de integridad permite detectar alteraciones de la cadena.

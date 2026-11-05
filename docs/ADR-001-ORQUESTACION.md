# ADR-001: n8n como orquestador del proceso

Estado: aceptado para el cierre P0.

## Decisión

n8n es el orquestador principal de la cadena diaria: dispara la recolección, obtiene los datos oficiales de HIBP, coordina correlación, contención, notificación y auditoría mediante sub-workflows. FastAPI permanece como API de negocio, persistencia transaccional y punto de acceso del frontend.

El scheduler interno de FastAPI conserva únicamente tareas auxiliares (reintentos/verificación) y no registra la recolección diaria por defecto: `BACKEND_SCHEDULER_COLLECT_ENABLED=false`. Esto evita dos procesos ejecutando detección y contención simultáneamente.

## Caché HIBP

El cliente HIBP de FastAPI mantiene Redis para llamadas de servicios de negocio y API. W01 conserva su caché PostgreSQL existente porque el workflow actual consulta HIBP directamente y necesita reanudar una ejecución n8n sin repetir la consulta. W02 obtiene el catálogo mediante el endpoint oficial `/breaches`; el nodo placeholder fue eliminado. La convergencia futura a una única ruta FastAPI requerirá una prueba de contrato y no se realiza como parte del cierre P0.

## Consecuencias

- No debe activarse el job `collect` del scheduler FastAPI junto con W01.
- Las credenciales n8n se configuran fuera del repositorio.
- Las operaciones transaccionales y autorización de la API siguen siendo responsabilidad de FastAPI; n8n no reemplaza RBAC.
- La prueba de humo de W01–W15 y la validación de credenciales siguen siendo tareas manuales de despliegue.

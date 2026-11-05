# Credenciales n8n requeridas

Validación: 2026-11-05, America/Lima. No se guardan secretos en este archivo.

## Credenciales detectadas en W01–W15

| Nombre esperado | Tipo n8n | Workflows | Campos requeridos | Obligatoria para demo | Sustitución segura |
|---|---|---|---|---|---|
| `Radar PG` (`radar_pg`) | PostgreSQL | W01, W02, W03, W04, W10, W11, W15 | Host accesible desde n8n, puerto, base de aplicación, usuario, contraseña y SSL según la red local | Sí para persistencia | No; usar una BD local de demo separada de `radar_test` |
| `HIBP API` (`radar_http_hibp`) | Header Auth | W01, W02, W11 | Header `hibp-api-key` con una API key válida y `User-Agent` configurado en el nodo | No | Fixture HTTP controlado o sandbox autorizado |
| `Radar SMTP` (`radar_smtp`) | SMTP | W06, W09, W15 | Host, puerto, TLS, usuario, contraseña y remitente | No | SMTP local de pruebas o mock de envío |

## Dependencias por variables de entorno

Los siguientes nodos no declaran una credencial n8n y consumen variables del contenedor:

- `RADAR_API_BASE`: W09 para generación/descarga de reportes.
- `IDP_WEBHOOK_URL`, `IDP_HMAC_SECRET`: W03 y W04 para reset/revocación.
- `IDP_USERS_ENDPOINT`, `IDP_BEARER_TOKEN`: W10 para sincronización de usuarios.
- `TEAMS_WEBHOOK`: W06 y W15 para alertas Teams.
- `ADMIN_EMAIL`: W06 y W09.
- `RADAR_SERVICE_TOKEN`: W07, W09 y W13. Es un token de servicio de prueba para llamadas n8n → FastAPI; no debe ser el password del administrador ni escribirse en workflows.

## Autenticación n8n → FastAPI

W07, W09 y W13 envían `Authorization: Bearer $env.RADAR_SERVICE_TOKEN`. FastAPI valida ese token exclusivamente en el endpoint interno de auditoría y en las rutas que se incorporen explícitamente para servicio. La variable se mantiene en `.env` ignorado por Git y debe rotarse antes de cualquier despliegue.

Para W09, la generación y descarga de reportes requieren además que el token tenga el alcance de servicio previsto por el backend. No se incrusta una contraseña de administrador en ningún workflow.

En esta validación son valores de prueba. `IDP_USERS_ENDPOINT=https://idp.example.test/users` no representa un IdP real y no debe presentarse como integración productiva.

## Pasos manuales en la UI antes del smoke test

1. Abrir [n8n local](http://localhost:5678) e iniciar sesión con la cuenta propietaria local.
2. Ir a **Credentials → Create New → Postgres**, asignar **Name: Radar PG** y configurar:
   - Host: `host.docker.internal`
   - Port: `55433`
   - Database: `radar_creds`
   - User: `radar`
   - Password: tomarla de la configuración local existente; no copiarla a Git ni a esta documentación.
   - SSL: desactivado únicamente para esta red local si la configuración del servidor no exige TLS.
   Usar el botón de prueba de credencial. No usar `radar_test`.
3. Ir a **Credentials → Create New → Header Auth**, asignar **Name: HIBP API**, configurar el header `hibp-api-key` solo si existe una clave HIBP autorizada. Si no existe, dejarla pendiente y usar fixture controlado.
4. Ir a **Credentials → Create New → SMTP**, asignar **Name: Radar SMTP** y usar únicamente un SMTP sandbox/local. No configurar un servidor de correo productivo.
5. Mantener `RADAR_SERVICE_TOKEN` en el entorno del contenedor n8n y el mismo valor de prueba en el entorno del backend; nunca escribirlo en un workflow. Antes de producción, rotarlo.
6. Obtener una cookie de sesión desde la UI autenticada y ejecutar, desde la raíz del repositorio, `N8N_SESSION_COOKIE='…' python3 n8n/scripts/remap_workflow_ids.py`. La cookie no debe guardarse ni compartirse. El script mantiene los 15 workflows inactivos.
7. Verificar en **Workflows** que W07, W09 y W13 muestran la versión corregida y que ningún cron/webhook esté activo antes de ejecutar una prueba controlada.

## PostgreSQL de workflow testing

La instancia n8n debe usar la base de aplicación local, no `radar_test`. Desde el contenedor, el host del backend/PostgreSQL debe resolverse mediante `host.docker.internal`; no se debe usar `localhost` del contenedor para acceder al host. La configuración actual del proyecto publica PostgreSQL local en el puerto `55433` y la base `radar_creds`; la contraseña se configura exclusivamente en n8n y `.env` ignorado por Git.

## Estado actual

- `Radar PG`: creada en la instancia y prueba de conexión exitosa. Usa la base operacional `radar_creds`, no `radar_test`.
- `Radar SMTP`: creada como sandbox local de prueba. La conexión no se verificó porque no existe un listener SMTP en el puerto configurado; no se enviaron mensajes.
- `HIBP API`: no configurada con una clave real. W01/W02/W11 permanecen como `REQUIERE CREDENCIAL EXTERNA` hasta usar una clave autorizada o fixture.
- Las referencias de subworkflows y las credenciales portables fueron remapeadas en la instancia mediante [`remap_workflow_ids.py`](../n8n/scripts/remap_workflow_ids.py). No se guardaron IDs ni secretos en los JSON canónicos.
# Evidencia de smoke local

La credencial `Radar PG` pasó `Connection tested successfully`, pero durante la ejecución de W01 la consulta operacional devolvió cero filas aun con el dominio sintético creado en la base local. Antes de repetir W01/W02 debe comprobarse el destino efectivo de la credencial; no se registra ni se imprime su contraseña.

`Radar SMTP` quedó apuntando al sandbox Mailpit local y W15 produjo ejecuciones exitosas con correo sintético. HIBP, Teams e IdP permanecen en modo fixture; no se configuraron servicios externos reales.

# Configuración reproducible

Los archivos [`backend/.env.example`](../backend/.env.example) y [`n8n/.env.example`](../n8n/.env.example) contienen placeholders no operativos. Copiar el archivo correspondiente a `.env`, sustituir los valores y mantener esos archivos fuera de Git.

## Backend

| Variable | Clasificación | Uso |
|---|---|---|
| `DATABASE_URL` | REQUERIDA | Conexión PostgreSQL de la aplicación y migraciones |
| `JWT_SECRET` | REQUERIDA | Firma JWT y cifrado de secretos MFA; mínimo 32 caracteres aleatorios |
| `HIBP_API_KEY` | REQUERIDA | Autenticación contra HIBP |
| `REDIS_URL` | REQUERIDA | Redis para caché HIBP y dependencias operativas |
| `REDIS_REQUIRED` | OPCIONAL | Si es `true`, `/ready` exige Redis disponible |
| `CORS_ORIGINS` | REQUERIDA | Lista JSON de orígenes permitidos, por ejemplo `["http://localhost:5173"]` |
| `APP_NAME`, `APP_ENV`, `APP_VERSION`, `TIMEZONE`, `API_V1_PREFIX` | OPCIONAL | Perfil, metadatos y prefijo API |
| `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, `MFA_CHALLENGE_EXPIRE_MINUTES`, `MFA_REQUIRED_ROLES`, `PASSWORD_MIN_LENGTH` | OPCIONAL | Seguridad y validación de credenciales |
| `N8N_SERVICE_TOKEN` | OPCIONAL | Token de servicio para el endpoint interno de auditoría usado por n8n; obligatorio si se habilitan W07/W09/W13 |
| `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_ECHO` | OPCIONAL | Pool y diagnóstico SQL |
| `HIBP_BASE_URL`, `HIBP_USER_AGENT`, `HIBP_RATE_LIMIT_SECONDS`, `HIBP_MAX_RETRIES`, `HIBP_BACKOFF_BASE`, `HIBP_CACHE_TTL_HOURS`, `RATE_LIMIT_PER_MINUTE` | OPCIONAL | Cliente y resiliencia HIBP |
| `IDP_PROVIDER` | OPCIONAL | `entra`, `ldap` o `generic_webhook` |
| `IDP_TENANT_ID`, `IDP_CLIENT_ID`, `IDP_CLIENT_SECRET` | OPCIONAL | IdP Entra |
| `IDP_WEBHOOK_URL`, `IDP_WEBHOOK_HMAC_SECRET` | OPCIONAL | IdP webhook genérico |
| `LDAP_SERVER`, `LDAP_BASE_DN`, `LDAP_BIND_DN`, `LDAP_BIND_PASSWORD` | OPCIONAL | IdP LDAP |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_USE_TLS` | OPCIONAL | Notificaciones por email |
| `TEAMS_WEBHOOK_URL`, `SLACK_WEBHOOK_URL` | OPCIONAL | Alertas de chat |
| `REPORTS_STORAGE_PATH`, `REPORTS_SIGNED_URL_TTL_SECONDS` | OPCIONAL | Almacenamiento de reportes |
| `RETRY_BACKOFF_SCHEDULE_MIN`, `RETRY_MAX_ATTEMPTS` | OPCIONAL | Reintentos de contención |
| `AUDIT_RETENTION_DAYS`, `AUDIT_VERIFY_INTERVAL_HOURS` | OPCIONAL | Retención/verificación de auditoría |
| `METRICS_ENABLED`, `LOG_LEVEL`, `LOG_JSON` | OPCIONAL | Observabilidad |
| `BACKEND_SCHEDULER_COLLECT_ENABLED` | SOLO DESARROLLO | Debe permanecer `false` con n8n para no duplicar recolección |
| `POSTGRES_PASSWORD`, `N8N_USER`, `N8N_PASSWORD` | SOLO DESARROLLO | Variables del Compose integrado |

## n8n

| Variable | Clasificación | Uso |
|---|---|---|
| `N8N_HOST`, `N8N_PORT`, `N8N_PROTOCOL`, `WEBHOOK_URL`, `GENERIC_TIMEZONE` | REQUERIDA | Runtime y URLs de n8n |
| `RADAR_API_BASE` | REQUERIDA | URL base para llamadas de workflows al backend |
| `RADAR_SERVICE_TOKEN` | OPCIONAL | Token de servicio enviado a FastAPI por W07/W09/W13; debe coincidir con `N8N_SERVICE_TOKEN` |
| `IDP_WEBHOOK_URL`, `IDP_HMAC_SECRET` | OPCIONAL | Contención IdP desde W03/W04 |
| `IDP_BEARER_TOKEN`, `IDP_USERS_ENDPOINT` | OPCIONAL | Sincronización W10 |
| `ADMIN_EMAIL` | OPCIONAL | Alertas y reportes administrativos |
| `TEAMS_WEBHOOK` | OPCIONAL | Alertas/notificaciones Teams |

Las credenciales de nodos PostgreSQL, SMTP y HIBP se configuran en el gestor de credenciales de n8n, no mediante JSON versionados. Los placeholders no deben utilizarse en producción.

## Producción

En producción se requiere un gestor de secretos, TLS para API/n8n/IdP, `BACKEND_SCHEDULER_COLLECT_ENABLED=false`, una política explícita de CORS y una instancia PostgreSQL/Redis separada de desarrollo. La contraseña histórica documentada en versiones anteriores de [`README.md`](../README.md) debe rotarse manualmente si fue utilizada.

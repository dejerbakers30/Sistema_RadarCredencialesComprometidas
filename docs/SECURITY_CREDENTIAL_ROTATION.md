# Rotación de credencial local

El 5 de noviembre de 2026 se detectó que una contraseña de desarrollo de PostgreSQL había aparecido accidentalmente en una salida de terminal durante la validación local.

La credencial del rol `radar` de la base `radar_creds` fue rotada. Se actualizaron el entorno local del backend y la credencial `Radar PG` de n8n, sin modificar el historial Git. Las conexiones del backend y de n8n fueron comprobadas sin mostrar el secreto.

La contraseña local del usuario administrador de n8n fue rotada antes de la corrida E2E. La sesión temporal utilizada para automatizar la API local fue cerrada mediante `/rest/logout` y sus archivos temporales fueron eliminados al finalizar.

No se incluyen contraseñas, tokens ni claves en este documento.

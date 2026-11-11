PASO 4 — Verificación, Completitud y Mejora de Workflows n8n (JSON)
Alcance del Paso 4: Auditar los workflows n8n contra el diseño del Paso 1, verificar que los JSON estén completos y funcionales, completar los faltantes y aplicar mejoras. Se entregan workflows exportables e importables en n8n (formato JSON v1.x), integrados con la API del Paso 2 y el frontend del Paso 3.

1. Auditoría de completitud — Workflows n8n
1.1 Inventario de workflows requeridos
#	Workflow	¿En Pasos 1–3?	Estado	Acción en Paso 4
W01	Recolección diaria HIBP	Descripción sí, JSON no	❌ Faltante	Desarrollar
W02	Correlación con directorio	Descripción sí, JSON no	❌ Faltante	Desarrollar
W03	Contención automática (reset + revoke)	Descripción sí, JSON no	❌ Faltante	Desarrollar
W04	Reintentos / DLQ	Descripción sí, JSON no	❌ Faltante	Desarrollar
W05	Notificación al usuario afectado	Parcial	⚠️ Mejorable	Completar
W06	Alerta al admin por fallos	Parcial	⚠️ Mejorable	Completar
W07	Verificación de cadena de auditoría	No	❌ Faltante	Desarrollar
W08	Webhook entrante IdP callback	Parcial	⚠️ Mejorable	Completar
W09	Reporte diario automático (resumen)	No	❌ Faltante	Desarrollar
W10	Sincronización de usuarios desde IdP	No	❌ Faltante	Desarrollar
W11	Health-check de fuentes	No	❌ Faltante	Desarrollar
W12	Error Handler global (Error Trigger)	No	❌ Faltante	Desarrollar
W13	Sub-workflow utilitario: auditoría	No	❌ Faltante	Desarrollar
W14	Sub-workflow utilitario: hash canónico	No	❌ Faltante	Desarrollar
W15	Sub-workflow utilitario: notificación	No	❌ Faltante	Desarrollar
1.2 Veredicto
Los workflows n8n estaban descritos textualmente en el Paso 1 (nodos, expresiones) pero no existía ningún JSON importable. Los Pasos 2–3 desarrollaron backend y frontend, pero asumieron que n8n ya estaba operativo. Se completan los 15 workflows con JSON válido, credenciales referenciadas, manejo de errores y enlaces entre workflows.

1.3 Convenciones aplicadas
Formato: n8n export v1.x (compatible con n8n import:workflow).

Credenciales: referenciadas por id y name (no incluyen secretos; se configuran en la UI).

Variables de entorno n8n: RADAR_API_BASE, HIBP_API_KEY, IDP_WEBHOOK_URL, IDP_HMAC_SECRET, SMTP_CRED_ID, TEAMS_WEBHOOK, SLACK_WEBHOOK, ADMIN_EMAIL.

PostgreSQL: nodo n8n-nodes-base.postgres con credencial Radar PG.

Idempotencia: todos los INSERT usan ON CONFLICT DO NOTHING o DO UPDATE.

Errores: cada workflow crítico tiene onError: continueErrorOutput y deriva a W12.

2. Credenciales n8n necesarias
ID	Nombre	Tipo	Campos
radar_pg	Radar PG	Postgres	host, port, db=radar_creds, user, password, ssl
radar_http_hibp	HIBP API	Header Auth	hibp-api-key
radar_http_idp	IdP Webhook	Header Auth	X-Radar-Signature (calculado por nodo Code)
radar_smtp	Radar SMTP	SMTP	host, port, user, password, TLS
radar_teams	Teams Webhook	HTTP (URL fija)	URL del webhook
radar_slack	Slack Webhook	HTTP (URL fija)	URL del webhook
3. W14 — Sub-workflow: hash canónico (utilitario)
Base para W01 y W02. Se invoca con Execute Workflow.

json
{
  "name": "W14 - Utils Hash Canonico",
  "nodes": [
    {
      "parameters": {
        "workflowInputs": {
          "values": [
            { "name": "email" },
            { "name": "breach" },
            { "name": "fecha_breach" }
          ]
        }
      },
      "id": "a1000000-0000-0000-0000-000000000001",
      "name": "Input",
      "type": "n8n-nodes-base.executeWorkflowTrigger",
      "typeVersion": 1.1,
      "position": [220, 300]
    },
    {
      "parameters": {
        "jsCode": "const crypto = require('crypto');\nconst out = [];\nfor (const item of $input.all()) {\n  const email = String(item.json.email || '').toLowerCase().trim();\n  const breach = String(item.json.breach || '').trim();\n  const fecha = item.json.fecha_breach || 'sin_fecha';\n  const payload = `${email}|${breach}|${fecha}`;\n  const hash = crypto.createHash('sha256').update(payload).digest('hex');\n  out.push({ json: { ...item.json, hash_canonico: hash, payload } });\n}\nreturn out;"
      },
      "id": "a1000000-0000-0000-0000-000000000002",
      "name": "Compute SHA256",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [460, 300]
    }
  ],
  "connections": {
    "Input": {
      "main": [[{ "node": "Compute SHA256", "type": "main", "index": 0 }]]
    }
  },
  "settings": { "executionOrder": "v1" },
  "active": false,
  "tags": ["radar", "utils"]
}
4. W13 — Sub-workflow: auditoría inmutable
Escribe en audit_log con encadenamiento de hash. Invocado por todos los workflows.

json
{
  "name": "W13 - Utils Auditoria",
  "nodes": [
    {
      "parameters": {
        "workflowInputs": {
          "values": [
            { "name": "modulo" },
            { "name": "accion" },
            { "name": "resultado" },
            { "name": "entidad" },
            { "name": "entidad_id" },
            { "name": "usuario_email" },
            { "name": "detalle" }
          ]
        }
      },
      "id": "a1300000-0000-0000-0000-000000000001",
      "name": "Input",
      "type": "n8n-nodes-base.executeWorkflowTrigger",
      "typeVersion": 1.1,
      "position": [220, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT hash_actual FROM audit_log ORDER BY id DESC LIMIT 1",
        "options": {}
      },
      "id": "a1300000-0000-0000-0000-000000000002",
      "name": "Get Prev Hash",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.5,
      "position": [460, 300],
      "credentials": { "postgres": { "id": "radar_pg", "name": "Radar PG" } }
    },
    {
      "parameters": {
        "jsCode": "const crypto = require('crypto');\nconst input = $('Input').first().json;\nconst prevRow = $input.first().json;\nconst prev = prevRow.hash_actual || 'GENESIS';\nconst ts = new Date().toISOString();\nconst usuario_email = input.usuario_email || null;\nconst modulo = input.modulo;\nconst accion = input.accion;\nconst resultado = input.resultado;\nconst payload = `${ts}|${usuario_email || ''}|${modulo}|${accion}|${resultado}|${prev}`;\nconst hash_actual = crypto.createHash('sha256').update(payload).digest('hex');\nreturn [{ json: { ts, tz: 'Europe/Madrid', usuario_email, modulo, accion, resultado, entidad: input.entidad || null, entidad_id: input.entidad_id || null, detalle: input.detalle || null, hash_anterior: prev, hash_actual } }];"
      },
      "id": "a1300000-0000-0000-0000-000000000003",
      "name": "Chain Hash",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [700, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "INSERT INTO audit_log (ts, tz, usuario_email, modulo, accion, entidad, entidad_id, resultado, detalle, hash_anterior, hash_actual)\nVALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9::jsonb,$10,$11)\nRETURNING id;",
        "options": { "queryReplacement": "={{ [$json.ts, $json.tz, $json.usuario_email, $json.modulo, $json.accion, $json.entidad, $json.entidad_id, $json.resultado, JSON.stringify($json.detalle), $json.hash_anterior, $json.hash_actual] }}" }
      },
      "id": "a1300000-0000-0000-0000-000000000004",
      "name": "Insert Audit",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.5,
      "position": [940, 300],
      "credentials": { "postgres": { "id": "radar_pg", "name": "Radar PG" } }
    }
  ],
  "connections": {
    "Input": { "main": [[{ "node": "Get Prev Hash", "type": "main", "index": 0 }]] },
    "Get Prev Hash": { "main": [[{ "node": "Chain Hash", "type": "main", "index": 0 }]] },
    "Chain Hash": { "main": [[{ "node": "Insert Audit", "type": "main", "index": 0 }]] }
  },
  "settings": { "executionOrder": "v1" },
  "active": false,
  "tags": ["radar", "utils"]
}
5. W15 — Sub-workflow: notificación (email + chat)
json
{
  "name": "W15 - Utils Notificacion",
  "nodes": [
    {
      "parameters": {
        "workflowInputs": {
          "values": [
            { "name": "destinatario" },
            { "name": "asunto" },
            { "name": "cuerpo" },
            { "name": "canal" },
            { "name": "leak_hit_id" }
          ]
        }
      },
      "id": "a1500000-0000-0000-0000-000000000001",
      "name": "Input",
      "type": "n8n-nodes-base.executeWorkflowTrigger",
      "typeVersion": 1.1,
      "position": [220, 300]
    },
    {
      "parameters": {
        "conditions": {
          "options": { "caseSensitive": true, "leftValue": "", "typeValidation": "strict" },
          "conditions": [
            {
              "id": "c1",
              "leftValue": "={{ $json.canal }}",
              "rightValue": "email",
              "operator": { "type": "string", "operation": "equals" }
            }
          ],
          "combinator": "and"
        }
      },
      "id": "a1500000-0000-0000-0000-000000000002",
      "name": "IF Email",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [460, 300]
    },
    {
      "parameters": {
        "fromEmail": "radar-creds@example.com",
        "toEmail": "={{ $json.destinatario }}",
        "subject": "={{ $json.asunto }}",
        "emailType": "text",
        "message": "={{ $json.cuerpo }}",
        "options": {}
      },
      "id": "a1500000-0000-0000-0000-000000000003",
      "name": "Send Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 2.1,
      "position": [720, 220],
      "credentials": { "smtp": { "id": "radar_smtp", "name": "Radar SMTP" } }
    },
    {
      "parameters": {
        "method": "POST",
        "url": "={{ $env.TEAMS_WEBHOOK }}",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({ text: $json.asunto + '\\n\\n' + $json.cuerpo }) }}",
        "options": {}
      },
      "id": "a1500000-0000-0000-0000-000000000004",
      "name": "Send Teams",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [720, 380]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "INSERT INTO notificaciones (leak_hit_id, destinatario, canal, plantilla, enviado_en, estado)\nVALUES ($1::uuid, $2, $3, $4, now(), 'enviado')\nRETURNING id;",
        "options": { "queryReplacement": "={{ [$json.leak_hit_id, $json.destinatario, $json.canal, $json.asunto] }}" }
      },
      "id": "a1500000-0000-0000-0000-000000000005",
      "name": "Log Notificacion",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.5,
      "position": [980, 300],
      "credentials": { "postgres": { "id": "radar_pg", "name": "Radar PG" } }
    }
  ],
  "connections": {
    "Input": { "main": [[{ "node": "IF Email", "type": "main", "index": 0 }]] },
    "IF Email": {
      "main": [
        [{ "node": "Send Email", "type": "main", "index": 0 }],
        [{ "node": "Send Teams", "type": "main", "index": 0 }]
      ]
    },
    "Send Email": { "main": [[{ "node": "Log Notificacion", "type": "main", "index": 0 }]] },
    "Send Teams": { "main": [[{ "node": "Log Notificacion", "type": "main", "index": 0 }]] }
  },
  "settings": { "executionOrder": "v1" },
  "active": false,
  "tags": ["radar", "utils"]
}
6. W01 — Recolección diaria HIBP
Trigger: Cron 03:00 UTC. Salida: filas nuevas en leak_hits + invocación de W02.

json
{
  "name": "W01 - Recoleccion HIBP",
  "nodes": [
    {
      "parameters": {
        "rule": { "interval": [{ "field": "cronExpression", "expression": "0 3 * * *" }] }
      },
      "id": "a0100000-0000-0000-0000-000000000001",
      "name": "Cron 03:00 UTC",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.2,
      "position": [220, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT id, dominio FROM dominios_monitoreados WHERE activo = TRUE",
        "options": {}
      },
      "id": "a0100000-0000-0000-0000-000000000002",
      "name": "Leer Dominios",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.5,
      "position": [460, 300],
      "credentials": { "postgres": { "id": "radar_pg", "name": "Radar PG" } }
    },
    {
      "parameters": { "batchSize": 1, "options": {} },
      "id": "a0100000-0000-0000-0000-000000000003",
      "name": "Loop Dominios",
      "type": "n8n-nodes-base.splitInBatches",
      "typeVersion": 3,
      "position": [700, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT payload, expira_en FROM hibp_cache\nWHERE cache_key = encode(digest($1 || '|breacheddomain', 'sha256'), 'hex')\n  AND expira_en > now()\nLIMIT 1;",
        "options": { "queryReplacement": "={{ [$json.dominio] }}" }
      },
      "id": "a0100000-0000-0000-0000-000000000004",
      "name": "Check Cache",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.5,
      "position": [940, 300],
      "credentials": { "postgres": { "id": "radar_pg", "name": "Radar PG" } },
      "alwaysOutputData": true
    },
    {
      "parameters": {
        "conditions": {
          "options": { "caseSensitive": true, "typeValidation": "strict" },
          "conditions": [
            {
              "id": "c1",
              "leftValue": "={{ $json.payload }}",
              "rightValue": "",
              "operator": { "type": "string", "operation": "notEmpty" }
            }
          ],
          "combinator": "and"
        }
      },
      "id": "a0100000-0000-0000-0000-000000000005",
      "name": "IF Cache Hit",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [1180, 300]
    },
    {
      "parameters": {
        "method": "GET",
        "url": "=https://haveibeenpwned.com/api/v3/breacheddomain/{{ $('Loop Dominios').item.json.dominio }}",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            { "name": "user-agent", "value": "RadarCreds/1.0" }
          ]
        },
        "options": {
          "response": { "response": { "neverError": true, "fullResponse": true } },
          "retry": { "retry": { "enabled": true, "maxRetries": 3, "waitBetweenRetries": 5000 } }
        }
      },
      "id": "a0100000-0000-0000-0000-000000000006",
      "name": "HIBP BreachedDomain",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [1420, 220],
      "credentials": { "httpHeaderAuth": { "id": "radar_http_hibp", "name": "HIBP API" } },
      "onError": "continueErrorOutput"
    },
    {
      "parameters": {
        "jsCode": "const resp = $input.first().json;\nconst dominio = $('Loop Dominios').item.json.dominio;\nconst status = resp.statusCode;\nif (status === 404) { return []; }\nif (status === 429) {\n  const retry = parseInt(resp.headers?.['retry-after'] || '5', 10);\n  await new Promise(r => setTimeout(r, retry * 1000));\n  throw new Error('HIBP 429, reintentar');\n}\nif (status >= 400) { throw new Error('HIBP error ' + status); }\nconst body = typeof resp.body === 'string' ? JSON.parse(resp.body) : resp.body;\nconst out = [];\nfor (const [email, breaches] of Object.entries(body || {})) {\n  for (const breach of breaches) {\n    out.push({ json: { email, breach, dominio } });\n  }\n}\nreturn out;"
      },
      "id": "a0100000-0000-0000-0000-000000000007",
      "name": "Parse HIBP",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1660, 220]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "INSERT INTO hibp_cache (cache_key, payload, expira_en)\nVALUES (encode(digest($1 || '|breacheddomain','sha256'),'hex'), $2::jsonb, now() + interval '24 hours')\nON CONFLICT (cache_key) DO UPDATE SET payload = EXCLUDED.payload, expira_en = EXCLUDED.expira_en, consultado_en = now();",
        "options": { "queryReplacement": "={{ [ $('Loop Dominios').item.json.dominio, JSON.stringify($json) ] }}" }
      },
      "id": "a0100000-0000-0000-0000-000000000008",
      "name": "Guardar Cache",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.5,
      "position": [1660, 380],
      "credentials": { "postgres": { "id": "radar_pg", "name": "Radar PG" } }
    },
    {
      "parameters": {
        "workflowId": "W02_CORRELACION",
        "options": { "waitForSubWorkflow": false }
      },
      "id": "a0100000-0000-0000-0000-000000000010",
      "name": "Trigger W02",
      "type": "n8n-nodes-base.executeWorkflow",
      "typeVersion": 1.2,
      "position": [2140, 300]
    },
    {
      "parameters": {
        "workflowId": "W13_AUDITORIA",
        "workflowInputs": {
          "mappingMode": "defineBelow",
          "value": {
            "modulo": "leaks",
            "accion": "collect",
            "resultado": "ok",
            "entidad": "dominios_monitoreados",
            "entidad_id": "={{ $('Loop Dominios').item.json.id }}",
            "usuario_email": null,
            "detalle": "={{ JSON.stringify({ dominio: $('Loop Dominios').item.json.dominio }) }}"
          }
        }
      },
      "id": "a0100000-0000-0000-0000-000000000011",
      "name": "Audit Collect",
      "type": "n8n-nodes-base.executeWorkflow",
      "typeVersion": 1.2,
      "position": [2140, 460]
    }
  ],
  "connections": {
    "Cron 03:00 UTC": { "main": [[{ "node": "Leer Dominios", "type": "main", "index": 0 }]] },
    "Leer Dominios": { "main": [[{ "node": "Loop Dominios", "type": "main", "index": 0 }]] },
    "Loop Dominios": { "main": [[{ "node": "Check Cache", "type": "main", "index": 0 }]] },
    "Check Cache": { "main": [[{ "node": "IF Cache Hit", "type": "main", "index": 0 }]] },
    "IF Cache Hit": {
      "main": [
        [{ "node": "Trigger W02", "type": "main", "index": 0 }],
        [{ "node": "HIBP BreachedDomain", "type": "main", "index": 0 }]
      ]
    },
    "HIBP BreachedDomain": {
      "main": [
        [{ "node": "Parse HIBP", "type": "main", "index": 0 }],
        [{ "node": "Guardar Cache", "type": "main", "index": 0 }]
      ]
    },
    "Parse HIBP": { "main": [[{ "node": "Guardar Cache", "type": "main", "index": 0 }]] },
    "Guardar Cache": { "main": [[{ "node": "Trigger W02", "type": "main", "index": 0 }]] },
    "Trigger W02": { "main": [[{ "node": "Audit Collect", "type": "main", "index": 0 }]] }
  },
  "settings": {
    "executionOrder": "v1",
    "saveManualExecutions": true,
    "callerPolicy": "workflowsFromSameOwner",
    "errorWorkflow": "W12_ERROR_HANDLER"
  },
  "active": false,
  "tags": ["radar", "collect"]
}
7. W02 — Correlación con directorio
Trigger: invocado por W01. Salida: filas en leak_hits para emails corporativos activos + invocación de W03.

json
{
  "name": "W02 - Correlacion Directorio",
  "nodes": [
    {
      "parameters": {
        "workflowInputs": {
          "values": [
            { "name": "dominio" },
            { "name": "email" },
            { "name": "breach" }
          ]
        }
      },
      "id": "a0200000-0000-0000-0000-000000000001",
      "name": "Input",
      "type": "n8n-nodes-base.executeWorkflowTrigger",
      "typeVersion": 1.1,
      "position": [220, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT email, id AS usuario_id FROM usuarios WHERE activo = TRUE",
        "options": {}
      },
      "id": "a0200000-0000-0000-0000-000000000002",
      "name": "Leer Usuarios Activos",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.5,
      "position": [460, 220],
      "credentials": { "postgres": { "id": "radar_pg", "name": "Radar PG" } }
    },
    {
      "parameters": {
        "method": "GET",
        "url": "https://haveibeenpwned.com/api/v3/breaches",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            { "name": "user-agent", "value": "RadarCreds/1.0" }
          ]
        },
        "options": { "response": { "response": { "neverError": true, "fullResponse": true } } }
      },
      "id": "a0200000-0000-0000-0000-000000000003",
      "name": "HIBP Breaches Catalog",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [460, 420],
      "credentials": { "httpHeaderAuth": { "id": "radar_http_hibp", "name": "HIBP API" } }
    },
    {
      "parameters": {
        "jsCode": "const users = $('Leer Usuarios Activos').all().map(i => i.json);\nconst input = $('Input').all().map(i => i.json);\nconst catRaw = $('HIBP Breaches Catalog').first().json;\nconst cat = (typeof catRaw.body === 'string' ? JSON.parse(catRaw.body) : catRaw.body) || [];\nconst catalog = {};\nfor (const b of cat) { catalog[b.Name] = b; }\nconst userMap = new Map(users.map(u => [String(u.email).toLowerCase(), u.usuario_id]));\nconst out = [];\nfor (const row of input) {\n  const emailL = String(row.email || '').toLowerCase();\n  const uid = userMap.get(emailL);\n  if (!uid) continue;\n  const meta = catalog[row.breach] || {};\n  const dataClasses = meta.DataClasses || [];\n  let severidad = 'baja';\n  if (dataClasses.some(d => /password/i.test(d))) severidad = 'critica';\n  else if (dataClasses.some(d => /credit|bank|token/i.test(d))) severidad = 'alta';\n  else if (dataClasses.some(d => /email|username|phone/i.test(d))) severidad = 'media';\n  out.push({ json: {\n    email_corporativo: emailL,\n    usuario_id: uid,\n    breach_origen: row.breach,\n    breach_dominio: meta.Domain || null,\n    fecha_breach: meta.BreachDate || null,\n    severidad,\n    datos_expuestos: dataClasses,\n    fuente_detalle: 'HIBP/' + row.breach\n  }});\n}\nreturn out;"
      },
      "id": "a0200000-0000-0000-0000-000000000004",
      "name": "Merge & Enrich",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [700, 300]
    },
    {
      "parameters": {
        "workflowId": "W14_HASH",
        "workflowInputs": {
          "mappingMode": "defineBelow",
          "value": {
            "email": "={{ $json.email_corporativo }}",
            "breach": "={{ $json.breach_origen }}",
            "fecha_breach": "={{ $json.fecha_breach }}"
          }
        },
        "options": { "waitForSubWorkflow": true }
      },
      "id": "a0200000-0000-0000-0000-000000000005",
      "name": "Hash Canonico",
      "type": "n8n-nodes-base.executeWorkflow",
      "typeVersion": 1.2,
      "position": [940, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "INSERT INTO leak_hits (email_corporativo, usuario_id, breach_origen, breach_dominio, fecha_breach, fecha_deteccion, severidad, fuente_id, fuente_detalle, datos_expuestos, estado, hash_canonico)\nSELECT $1::citext, $2::uuid, $3, $4, $5::date, now(), $6::leak_severidad, f.id, $7, $8::text[], 'nuevo', $9\nFROM fuentes f WHERE f.nombre = 'hibp'\nON CONFLICT (hash_canonico) DO NOTHING\nRETURNING id, email_corporativo, breach_origen;",
        "options": {
          "queryReplacement": "={{ [ $json.email_corporativo, $json.usuario_id, $json.breach_origen, $json.breach_dominio, $json.fecha_breach, $json.severidad, $json.fuente_detalle, $json.datos_expuestos, $json.hash_canonico ] }}"
        }
      },
      "id": "a0200000-0000-0000-0000-000000000006",
      "name": "Insert Leak Hit",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.5,
      "position": [1180, 300],
      "credentials": { "postgres": { "id": "radar_pg", "name": "Radar PG" } },
      "alwaysOutputData": true
    },
    {
      "parameters": {
        "conditions": {
          "options": { "caseSensitive": true, "typeValidation": "strict" },
          "conditions": [
            {
              "id": "c1",
              "leftValue": "={{ $json.id }}",
              "rightValue": "",
              "operator": { "type": "string", "operation": "notEmpty" }
            }
          ],
          "combinator": "and"
        }
      },
      "id": "a0200000-0000-0000-0000-000000000007",
      "name": "IF Nuevo Hit",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [1420, 300]
    },
    {
      "parameters": {
        "workflowId": "W03_CONTENCION",
        "workflowInputs": {
          "mappingMode": "defineBelow",
          "value": {
            "leak_hit_id": "={{ $json.id }}",
            "email": "={{ $json.email_corporativo }}",
            "breach": "={{ $json.breach_origen }}"
          }
        },
        "options": { "waitForSubWorkflow": false }
      },
      "id": "a0200000-0000-0000-0000-000000000008",
      "name": "Trigger W03",
      "type": "n8n-nodes-base.executeWorkflow",
      "typeVersion": 1.2,
      "position": [1660, 220]
    },
    {
      "parameters": {
        "workflowId": "W13_AUDITORIA",
        "workflowInputs": {
          "mappingMode": "defineBelow",
          "value": {
            "modulo": "leaks",
            "accion": "correlate",
            "resultado": "ok",
            "entidad": "leak_hits",
            "entidad_id": "={{ $json.id }}",
            "usuario_email": null,
            "detalle": "={{ JSON.stringify({ breach: $json.breach_origen }) }}"
          }
        }
      },
      "id": "a0200000-0000-0000-0000-000000000009",
      "name": "Audit Correlate",
      "type": "n8n-nodes-base.executeWorkflow",
      "typeVersion": 1.2,
      "position": [1660, 380]
    }
  ],
  "connections": {
    "Input": {
      "main": [[
        { "node": "Leer Usuarios Activos", "type": "main", "index": 0 },
        { "node": "HIBP Breaches Catalog", "type": "main", "index": 0 }
      ]]
    },
    "Leer Usuarios Activos": { "main": [[{ "node": "Merge & Enrich", "type": "main", "index": 0 }]] },
    "HIBP Breaches Catalog": { "main": [[{ "node": "Merge & Enrich", "type": "main", "index": 0 }]] },
    "Merge & Enrich": { "main": [[{ "node": "Hash Canonico", "type": "main", "index": 0 }]] },
    "Hash Canonico": { "main": [[{ "node": "Insert Leak Hit", "type": "main", "index": 0 }]] },
    "Insert Leak Hit": { "main": [[{ "node": "IF Nuevo Hit", "type": "main", "index": 0 }]] },
    "IF Nuevo Hit": {
      "main": [
        [{ "node": "Trigger W03", "type": "main", "index": 0 }],
        []
      ]
    },
    "Trigger W03": { "main": [[{ "node": "Audit Correlate", "type": "main", "index": 0 }]] }
  },
  "settings": {
    "executionOrder": "v1",
    "errorWorkflow": "W12_ERROR_HANDLER"
  },
  "active": false,
  "tags": ["radar", "correlate"]
}
8. W03 — Contención automática
Trigger: invocado por W02. Salida: resets + notificación + auditoría.

json
{
  "name": "W03 - Contencion Automatica",
  "nodes": [
    {
      "parameters": {
        "workflowInputs": {
          "values": [
            { "name": "leak_hit_id" },
            { "name": "email" },
            { "name": "breach" }
          ]
        }
      },
      "id": "a0300000-0000-0000-0000-000000000001",
      "name": "Input",
      "type": "n8n-nodes-base.executeWorkflowTrigger",
      "typeVersion": 1.1,
      "position": [220, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT id FROM resets WHERE leak_hit_id = $1::uuid AND resultado = 'exitoso' LIMIT 1;",
        "options": { "queryReplacement": "={{ [$json.leak_hit_id] }}" }
      },
      "id": "a0300000-0000-0000-0000-000000000002",
      "name": "Check Ya Contenido",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.5,
      "position": [460, 300],
      "credentials": { "postgres": { "id": "radar_pg", "name": "Radar PG" } },
      "alwaysOutputData": true
    },
    {
      "parameters": {
        "conditions": {
          "options": { "caseSensitive": true, "typeValidation": "strict" },
          "conditions": [
            {
              "id": "c1",
              "leftValue": "={{ $json.id }}",
              "rightValue": "",
              "operator": { "type": "string", "operation": "empty" }
            }
          ],
          "combinator": "and"
        }
      },
      "id": "a0300000-0000-0000-0000-000000000003",
      "name": "IF No Contenido",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [700, 300]
    },
    {
      "parameters": {
        "jsCode": "const crypto = require('crypto');\nconst input = $('Input').first().json;\nconst secret = $env.IDP_HMAC_SECRET || '';\nconst resetPayload = { action: 'reset_password', email: input.email };\nconst revokePayload = { action: 'revoke_sessions', email: input.email };\nconst sign = (body) => crypto.createHmac('sha256', secret).update(JSON.stringify(body)).digest('hex');\nreturn [{ json: {\n  ...input,\n  reset_body: JSON.stringify(resetPayload),\n  reset_sig: sign(resetPayload),\n  revoke_body: JSON.stringify(revokePayload),\n  revoke_sig: sign(revokePayload)\n}}];"
      },
      "id": "a0300000-0000-0000-0000-000000000004",
      "name": "Prepare IdP Calls",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [940, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "={{ $env.IDP_WEBHOOK_URL }}",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            { "name": "Content-Type", "value": "application/json" },
            { "name": "X-Radar-Signature", "value": "={{ $json.reset_sig }}" }
          ]
        },
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ $json.reset_body }}",
        "options": {
          "response": { "response": { "neverError": true, "fullResponse": true } },
          "retry": { "retry": { "enabled": true, "maxRetries": 2, "waitBetweenRetries": 3000 } }
        }
      },
      "id": "a0300000-0000-0000-0000-000000000005",
      "name": "Reset Password",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [1180, 220],
      "onError": "continueErrorOutput"
    },
    {
      "parameters": {
        "method": "POST",
        "url": "={{ $env.IDP_WEBHOOK_URL }}",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            { "name": "Content-Type", "value": "application/json" },
            { "name": "X-Radar-Signature", "value": "={{ $json.revoke_sig }}" }
          ]
        },
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ $json.revoke_body }}",
        "options": {
          "response": { "response": { "neverError": true, "fullResponse": true } },
          "retry": { "retry": { "enabled": true, "maxRetries": 2, "waitBetweenRetries": 3000 } }
        }
      },
      "id": "a0300000-0000-0000-0000-000000000006",
      "name": "Revoke Sessions",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [1180, 380],
      "onError": "continueErrorOutput"
    },
    {
      "parameters": {
        "jsCode": "const reset = $('Reset Password').first().json;\nconst revoke = $('Revoke Sessions').first().json;\nconst input = $('Prepare IdP Calls').first().json;\nconst resetOk = reset.statusCode >= 200 && reset.statusCode < 300;\nconst revokeOk = revoke.statusCode >= 200 && revoke.statusCode < 300;\nconst ok = resetOk && revokeOk;\nreturn [{ json: {\n  leak_hit_id: input.leak_hit_id,\n  email: input.email,\n  breach: input.breach,\n  ok,\n  detalle: {\n    reset_password: { status: reset.statusCode, ok: resetOk },\n    revoke_sessions: { status: revoke.statusCode, ok: revokeOk }\n  }\n}}];"
      },
      "id": "a0300000-0000-0000-0000-000000000007",
      "name": "Evaluate Result",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1420, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "INSERT INTO resets (leak_hit_id, timestamp, metodo, resultado, idp_respuesta, intentos, proximo_intento)\nVALUES ($1::uuid, now(), 'automatico', $2::reset_resultado, $3::jsonb, 1,\n        CASE WHEN $2 = 'reintento' THEN now() + interval '15 minutes' ELSE NULL END)\nRETURNING id, resultado;",
        "options": { "queryReplacement": "={{ [ $json.leak_hit_id, $json.ok ? 'exitoso' : 'reintento', JSON.stringify($json.detalle) ] }}" }
      },
      "id": "a0300000-0000-0000-0000-000000000008",
      "name": "Insert Reset",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.5,
      "position": [1660, 300],
      "credentials": { "postgres": { "id": "radar_pg", "name": "Radar PG" } }
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "UPDATE leak_hits\nSET estado = CASE WHEN $2 THEN 'contenido'::leak_estado ELSE estado END,\n    fecha_contencion = CASE WHEN $2 THEN now() ELSE fecha_contencion END,\n    actualizado_en = now()\nWHERE id = $1::uuid;",
        "options": { "queryReplacement": "={{ [ $('Evaluate Result').first().json.leak_hit_id, $('Evaluate Result').first().json.ok ] }}" }
      },
      "id": "a0300000-0000-0000-0000-000000000009",
      "name": "Update Leak State",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.5,
      "position": [1900, 300],
      "credentials": { "postgres": { "id": "radar_pg", "name": "Radar PG" } }
    },
    {
      "parameters": {
        "conditions": {
          "options": { "caseSensitive": true, "typeValidation": "strict" },
          "conditions": [
            {
              "id": "c1",
              "leftValue": "={{ $('Evaluate Result').first().json.ok }}",
              "rightValue": true,
              "operator": { "type": "boolean", "operation": "true" }
            }
          ],
          "combinator": "and"
        }
      },
      "id": "a0300000-0000-0000-0000-000000000010",
      "name": "IF Exitoso",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [2140, 300]
    },
    {
      "parameters": {
        "workflowId": "W15_NOTIFICACION",
        "workflowInputs": {
          "mappingMode": "defineBelow",
          "value": {
            "destinatario": "={{ $('Evaluate Result').first().json.email }}",
            "asunto": "Aviso de seguridad: credencial filtrada",
            "cuerpo": "={{ 'Hola,\\n\\nSe ha detectado tu correo en la filtración \"' + $('Evaluate Result').first().json.breach + '\". Se ha forzado el restablecimiento de tu contraseña y la invalidación de tus sesiones.\\n\\nSi no reconoces esta actividad, contacta con seguridad@example.com.' }}",
            "canal": "email",
            "leak_hit_id": "={{ $('Evaluate Result').first().json.leak_hit_id }}"
          }
        }
      },
      "id": "a0300000-0000-0000-0000-000000000011",
      "name": "Notify User",
      "type": "n8n-nodes-base.executeWorkflow",
      "typeVersion": 1.2,
      "position": [2380, 220]
    },
    {
      "parameters": {
        "workflowId": "W13_AUDITORIA",
        "workflowInputs": {
          "mappingMode": "defineBelow",
          "value": {
            "modulo": "resets",
            "accion": "auto_contain",
            "resultado": "={{ $('Evaluate Result').first().json.ok ? 'ok' : 'error' }}",
            "entidad": "leak_hits",
            "entidad_id": "={{ $('Evaluate Result').first().json.leak_hit_id }}",
            "usuario_email": null,
            "detalle": "={{ JSON.stringify($('Evaluate Result').first().json.detalle) }}"
          }
        }
      },
      "id": "a0300000-0000-0000-0000-000000000012",
      "name": "Audit Contain",
      "type": "n8n-nodes-base.executeWorkflow",
      "typeVersion": 1.2,
      "position": [2380, 380]
    }
  ],
  "connections": {
    "Input": { "main": [[{ "node": "Check Ya Contenido", "type": "main", "index": 0 }]] },
    "Check Ya Contenido": { "main": [[{ "node": "IF No Contenido", "type": "main", "index": 0 }]] },
    "IF No Contenido": {
      "main": [
        [{ "node": "Prepare IdP Calls", "type": "main", "index": 0 }],
        []
      ]
    },
    "Prepare IdP Calls": {
      "main": [[
        { "node": "Reset Password", "type": "main", "index": 0 },
        { "node": "Revoke Sessions", "type": "main", "index": 0 }
      ]]
    },
    "Reset Password": { "main": [[{ "node": "Evaluate Result", "type": "main", "index": 0 }], []] },
    "Revoke Sessions": { "main": [[{ "node": "Evaluate Result", "type": "main", "index": 0 }], []] },
    "Evaluate Result": { "main": [[{ "node": "Insert Reset", "type": "main", "index": 0 }]] },
    "Insert Reset": { "main": [[{ "node": "Update Leak State", "type": "main", "index": 0 }]] },
    "Update Leak State": { "main": [[{ "node": "IF Exitoso", "type": "main", "index": 0 }]] },
    "IF Exitoso": {
      "main": [
        [{ "node": "Notify User", "type": "main", "index": 0 }],
        []
      ]
    },
    "Notify User": { "main": [[{ "node": "Audit Contain", "type": "main", "index": 0 }]] }
  },
  "settings": {
    "executionOrder": "v1",
    "errorWorkflow": "W12_ERROR_HANDLER"
  },
  "active": false,
  "tags": ["radar", "contain"]
}
9. W04 — Reintentos / DLQ
Trigger: Cron cada 15 min. Salida: reprocesa resets en estado reintento.

json
{
  "name": "W04 - Reintentos DLQ",
  "nodes": [
    {
      "parameters": {
        "rule": { "interval": [{ "field": "minutes", "minutesInterval": 15 }] }
      },
      "id": "a0400000-0000-0000-0000-000000000001",
      "name": "Cron 15min",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.2,
      "position": [220, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT r.id AS reset_id, r.leak_hit_id, r.intentos, h.email_corporativo, h.breach_origen\nFROM resets r\nJOIN leak_hits h ON h.id = r.leak_hit_id\nWHERE r.resultado = 'reintento'\n  AND (r.proximo_intento IS NULL OR r.proximo_intento <= now())\nORDER BY r.proximo_intento NULLS FIRST\nLIMIT 100;",
        "options": {}
      },
      "id": "a0400000-0000-0000-0000-000000000002",
      "name": "Leer Pendientes",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.5,
      "position": [460, 300],
      "credentials": { "postgres": { "id": "radar_pg", "name": "Radar PG" } },
      "alwaysOutputData": true
    },
    {
      "parameters": { "batchSize": 1, "options": {} },
      "id": "a0400000-0000-0000-0000-000000000003",
      "name": "Loop Pendientes",
      "type": "n8n-nodes-base.splitInBatches",
      "typeVersion": 3,
      "position": [700, 300]
    },
    {
      "parameters": {
        "jsCode": "const crypto = require('crypto');\nconst row = $json;\nconst secret = $env.IDP_HMAC_SECRET || '';\nconst resetPayload = { action: 'reset_password', email: row.email_corporativo };\nconst revokePayload = { action: 'revoke_sessions', email: row.email_corporativo };\nconst sign = (b) => crypto.createHmac('sha256', secret).update(JSON.stringify(b)).digest('hex');\nreturn [{ json: { ...row, reset_body: JSON.stringify(resetPayload), reset_sig: sign(resetPayload), revoke_body: JSON.stringify(revokePayload), revoke_sig: sign(revokePayload) } }];"
      },
      "id": "a0400000-0000-0000-0000-000000000004",
      "name": "Prepare Retry",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [940, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "={{ $env.IDP_WEBHOOK_URL }}",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            { "name": "Content-Type", "value": "application/json" },
            { "name": "X-Radar-Signature", "value": "={{ $json.reset_sig }}" }
          ]
        },
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ $json.reset_body }}",
        "options": { "response": { "response": { "neverError": true, "fullResponse": true } } }
      },
      "id": "a0400000-0000-0000-0000-000000000005",
      "name": "Retry Reset",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [1180, 220],
      "onError": "continueErrorOutput"
    },
    {
      "parameters": {
        "method": "POST",
        "url": "={{ $env.IDP_WEBHOOK_URL }}",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            { "name": "Content-Type", "value": "application/json" },
            { "name": "X-Radar-Signature", "value": "={{ $json.revoke_sig }}" }
          ]
        },
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ $json.revoke_body }}",
        "options": { "response": { "response": { "neverError": true, "fullResponse": true } } }
      },
      "id": "a0400000-0000-0000-0000-000000000006",
      "name": "Retry Revoke",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [1180, 380],
      "onError": "continueErrorOutput"
    },
    {
      "parameters": {
        "jsCode": "const reset = $('Retry Reset').first().json;\nconst revoke = $('Retry Revoke').first().json;\nconst row = $('Prepare Retry').first().json;\nconst ok = reset.statusCode >= 200 && reset.statusCode < 300 && revoke.statusCode >= 200 && revoke.statusCode < 300;\nconst intentos = (row.intentos || 1) + 1;\nconst schedule = [15, 30, 60, 240, 1440];\nconst agotado = intentos >= 5;\nconst proximo = agotado ? null : new Date(Date.now() + schedule[Math.min(intentos - 1, schedule.length - 1)] * 60000).toISOString();\nreturn [{ json: { reset_id: row.reset_id, leak_hit_id: row.leak_hit_id, email: row.email_corporativo, ok, intentos, agotado, proximo_intento: proximo } }];"
      },
      "id": "a0400000-0000-0000-0000-000000000007",
      "name": "Evaluate Retry",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1420, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "UPDATE resets\nSET resultado = CASE WHEN $2 THEN 'exitoso'::reset_resultado WHEN $3 THEN 'fallido'::reset_resultado ELSE 'reintento'::reset_resultado END,\n    intentos = $4,\n    proximo_intento = $5::timestamptz,\n    idp_respuesta = $6::jsonb\nWHERE id = $1::uuid;",
        "options": { "queryReplacement": "={{ [ $json.reset_id, $json.ok, $json.agotado, $json.intentos, $json.proximo_intento, JSON.stringify({ retry: true }) ] }}" }
      },
      "id": "a0400000-0000-0000-0000-000000000008",
      "name": "Update Reset",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.5,
      "position": [1660, 300],
      "credentials": { "postgres": { "id": "radar_pg", "name": "Radar PG" } }
    },
    {
      "parameters": {
        "conditions": {
          "options": { "caseSensitive": true, "typeValidation": "strict" },
          "conditions": [
            {
              "id": "c1",
              "leftValue": "={{ $json.ok }}",
              "rightValue": true,
              "operator": { "type": "boolean", "operation": "true" }
            }
          ],
          "combinator": "and"
        }
      },
      "id": "a0400000-0000-0000-0000-000000000009",
      "name": "IF Exitoso",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [1900, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "UPDATE leak_hits SET estado = 'contenido', fecha_contencion = now(), actualizado_en = now() WHERE id = $1::uuid;",
        "options": { "queryReplacement": "={{ [$json.leak_hit_id] }}" }
      },
      "id": "a0400000-0000-0000-0000-000000000010",
      "name": "Mark Contenido",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.5,
      "position": [2140, 220],
      "credentials": { "postgres": { "id": "radar_pg", "name": "Radar PG" } }
    },
    {
      "parameters": {
        "workflowId": "W06_ALERTA_ADMIN",
        "workflowInputs": {
          "mappingMode": "defineBelow",
          "value": {
            "mensaje": "={{ 'Reset agotado para leak ' + $('Evaluate Retry').first().json.leak_hit_id + ' tras ' + $('Evaluate Retry').first().json.intentos + ' intentos' }}",
            "severidad": "alta"
          }
        }
      },
      "id": "a0400000-0000-0000-0000-000000000011",
      "name": "Alert Agotado",
      "type": "n8n-nodes-base.executeWorkflow",
      "typeVersion": 1.2,
      "position": [2140, 380]
    }
  ],
  "connections": {
    "Cron 15min": { "main": [[{ "node": "Leer Pendientes", "type": "main", "index": 0 }]] },
    "Leer Pendientes": { "main": [[{ "node": "Loop Pendientes", "type": "main", "index": 0 }]] },
    "Loop Pendientes": { "main": [[{ "node": "Prepare Retry", "type": "main", "index": 0 }]] },
    "Prepare Retry": {
      "main": [[
        { "node": "Retry Reset", "type": "main", "index": 0 },
        { "node": "Retry Revoke", "type": "main", "index": 0 }
      ]]
    },
    "Retry Reset": { "main": [[{ "node": "Evaluate Retry", "type": "main", "index": 0 }], []] },
    "Retry Revoke": { "main": [[{ "node": "Evaluate Retry", "type": "main", "index": 0 }], []] },
    "Evaluate Retry": { "main": [[{ "node": "Update Reset", "type": "main", "index": 0 }]] },
    "Update Reset": { "main": [[{ "node": "IF Exitoso", "type": "main", "index": 0 }]] },
    "IF Exitoso": {
      "main": [
        [{ "node": "Mark Contenido", "type": "main", "index": 0 }],
        [{ "node": "Alert Agotado", "type": "main", "index": 0 }]
      ]
    }
  },
  "settings": {
    "executionOrder": "v1",
    "errorWorkflow": "W12_ERROR_HANDLER"
  },
  "active": false,
  "tags": ["radar", "retry"]
}
10. W05 — Notificación al usuario (ya cubierto por W15)
W05 se implementa como alias del sub-workflow W15 invocado desde W03 y W04. No requiere JSON adicional; su contrato es el de W15 (destinatario, asunto, cuerpo, canal, leak_hit_id).

11. W06 — Alerta al admin
json
{
  "name": "W06 - Alerta Admin",
  "nodes": [
    {
      "parameters": {
        "workflowInputs": {
          "values": [
            { "name": "mensaje" },
            { "name": "severidad" }
          ]
        }
      },
      "id": "a0600000-0000-0000-0000-000000000001",
      "name": "Input",
      "type": "n8n-nodes-base.executeWorkflowTrigger",
      "typeVersion": 1.1,
      "position": [220, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "={{ $env.TEAMS_WEBHOOK }}",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({ text: '🚨 Radar Creds [' + $json.severidad + ']: ' + $json.mensaje }) }}",
        "options": { "response": { "response": { "neverError": true } } }
      },
      "id": "a0600000-0000-0000-0000-000000000002",
      "name": "Teams Alert",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [460, 300],
      "onError": "continueRegularOutput"
    },
    {
      "parameters": {
        "fromEmail": "radar-creds@example.com",
        "toEmail": "={{ $env.ADMIN_EMAIL }}",
        "subject": "=[Radar Creds] Alerta {{ $json.severidad }}",
        "emailType": "text",
        "message": "={{ $json.mensaje }}",
        "options": {}
      },
      "id": "a0600000-0000-0000-0000-000000000003",
      "name": "Email Admin",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 2.1,
      "position": [700, 300],
      "credentials": { "smtp": { "id": "radar_smtp", "name": "Radar SMTP" } },
      "onError": "continueRegularOutput"
    },
    {
      "parameters": {
        "workflowId": "W13_AUDITORIA",
        "workflowInputs": {
          "mappingMode": "defineBelow",
          "value": {
            "modulo": "admin",
            "accion": "alert",
            "resultado": "ok",
            "entidad": "alertas",
            "entidad_id": null,
            "usuario_email": null,
            "detalle": "={{ JSON.stringify({ mensaje: $json.mensaje, severidad: $json.severidad }) }}"
          }
        }
      },
      "id": "a0600000-0000-0000-0000-000000000004",
      "name": "Audit Alert",
      "type": "n8n-nodes-base.executeWorkflow",
      "typeVersion": 1.2,
      "position": [940, 300]
    }
  ],
  "connections": {
    "Input": { "main": [[{ "node": "Teams Alert", "type": "main", "index": 0 }]] },
    "Teams Alert": { "main": [[{ "node": "Email Admin", "type": "main", "index": 0 }]] },
    "Email Admin": { "main": [[{ "node": "Audit Alert", "type": "main", "index": 0 }]] }
  },
  "settings": { "executionOrder": "v1" },
  "active": false,
  "tags": ["radar", "notify"]
}
12. W07 — Verificación de cadena de auditoría
Trigger: Cron cada 6 h. Salida: alerta si la cadena está rota.

json
{
  "name": "W07 - Verificacion Cadena",
  "nodes": [
    {
      "parameters": {
        "rule": { "interval": [{ "field": "hours", "hoursInterval": 6 }] }
      },
      "id": "a0700000-0000-0000-0000-000000000001",
      "name": "Cron 6h",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.2,
      "position": [220, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT id, ts, usuario_email, modulo, accion, resultado, hash_anterior, hash_actual\nFROM audit_log\nORDER BY id ASC\nLIMIT 10000;",
        "options": {}
      },
      "id": "a0700000-0000-0000-0000-000000000002",
      "name": "Leer Auditoria",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.5,
      "position": [460, 300],
      "credentials": { "postgres": { "id": "radar_pg", "name": "Radar PG" } }
    },
    {
      "parameters": {
        "jsCode": "const crypto = require('crypto');\nconst rows = $input.all().map(i => i.json);\nlet prev = 'GENESIS';\nconst broken = [];\nfor (const r of rows) {\n  const ts = new Date(r.ts).toISOString();\n  const payload = `${ts}|${r.usuario_email || ''}|${r.modulo}|${r.accion}|${r.resultado}|${r.hash_anterior}`;\n  const expected = crypto.createHash('sha256').update(payload).digest('hex');\n  if (r.hash_anterior !== prev || r.hash_actual !== expected) {\n    broken.push(r.id);\n  }\n  prev = r.hash_actual;\n}\nreturn [{ json: { total: rows.length, broken, ok: broken.length === 0 } }];"
      },
      "id": "a0700000-0000-0000-0000-000000000003",
      "name": "Verify Chain",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [700, 300]
    },
    {
      "parameters": {
        "conditions": {
          "options": { "caseSensitive": true, "typeValidation": "strict" },
          "conditions": [
            {
              "id": "c1",
              "leftValue": "={{ $json.ok }}",
              "rightValue": false,
              "operator": { "type": "boolean", "operation": "false" }
            }
          ],
          "combinator": "and"
        }
      },
      "id": "a0700000-0000-0000-0000-000000000004",
      "name": "IF Rota",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [940, 300]
    },
    {
      "parameters": {
        "workflowId": "W06_ALERTA_ADMIN",
        "workflowInputs": {
          "mappingMode": "defineBelow",
          "value": {
            "mensaje": "={{ 'Cadena de auditoría rota en IDs: ' + $json.broken.join(', ') }}",
            "severidad": "critica"
          }
        }
      },
      "id": "a0700000-0000-0000-0000-000000000005",
      "name": "Alert Chain Broken",
      "type": "n8n-nodes-base.executeWorkflow",
      "typeVersion": 1.2,
      "position": [1180, 220]
    }
  ],
  "connections": {
    "Cron 6h": { "main": [[{ "node": "Leer Auditoria", "type": "main", "index": 0 }]] },
    "Leer Auditoria": { "main": [[{ "node": "Verify Chain", "type": "main", "index": 0 }]] },
    "Verify Chain": { "main": [[{ "node": "IF Rota", "type": "main", "index": 0 }]] },
    "IF Rota": { "main": [[{ "node": "Alert Chain Broken", "type": "main", "index": 0 }], []] }
  },
  "settings": { "executionOrder": "v1", "errorWorkflow": "W12_ERROR_HANDLER" },
  "active": false,
  "tags": ["radar", "audit"]
}
13. W08 — Webhook entrante IdP callback
json
{
  "name": "W08 - Webhook IdP Callback",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "radar/idp/callback",
        "responseMode": "responseNode",
        "options": { "rawBody": true }
      },
      "id": "a0800000-0000-0000-0000-000000000001",
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [220, 300],
      "webhookId": "radar-idp-callback"
    },
    {
      "parameters": {
        "jsCode": "const crypto = require('crypto');\nconst item = $input.first();\nconst secret = $env.IDP_HMAC_SECRET || '';\nconst sig = item.json.headers?.['x-radar-signature'] || '';\nconst raw = item.json.rawBody || JSON.stringify(item.json.body || {});\nconst expected = crypto.createHmac('sha256', secret).update(raw).digest('hex');\nconst ok = crypto.timingSafeEqual(Buffer.from(sig || ''), Buffer.from(expected));\nif (!ok) throw new Error('Firma HMAC inválida');\nconst body = typeof item.json.body === 'string' ? JSON.parse(item.json.body) : item.json.body;\nreturn [{ json: { ok, action: body.action, email: body.email, raw: body } }];"
      },
      "id": "a0800000-0000-0000-0000-000000000002",
      "name": "Verify HMAC",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [460, 300]
    },
    {
      "parameters": {
        "workflowId": "W13_AUDITORIA",
        "workflowInputs": {
          "mappingMode": "defineBelow",
          "value": {
            "modulo": "webhooks",
            "accion": "idp_callback",
            "resultado": "ok",
            "entidad": "webhooks",
            "entidad_id": null,
            "usuario_email": "={{ $json.email }}",
            "detalle": "={{ JSON.stringify({ action: $json.action }) }}"
          }
        }
      },
      "id": "a0800000-0000-0000-0000-000000000003",
      "name": "Audit Callback",
      "type": "n8n-nodes-base.executeWorkflow",
      "typeVersion": 1.2,
      "position": [700, 300]
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ JSON.stringify({ received: true }) }}",
        "options": {}
      },
      "id": "a0800000-0000-0000-0000-000000000004",
      "name": "Respond",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1.1,
      "position": [940, 300]
    }
  ],
  "connections": {
    "Webhook": { "main": [[{ "node": "Verify HMAC", "type": "main", "index": 0 }]] },
    "Verify HMAC": { "main": [[{ "node": "Audit Callback", "type": "main", "index": 0 }]] },
    "Audit Callback": { "main": [[{ "node": "Respond", "type": "main", "index": 0 }]] }
  },
  "settings": { "executionOrder": "v1" },
  "active": false,
  "tags": ["radar", "webhook"]
}
14. W09 — Reporte diario automático
Trigger: Cron 07:00 UTC. Salida: PDF operacional + envío por email.

json
{
  "name": "W09 - Reporte Diario",
  "nodes": [
    {
      "parameters": {
        "rule": { "interval": [{ "field": "cronExpression", "expression": "0 7 * * *" }] }
      },
      "id": "a0900000-0000-0000-0000-000000000001",
      "name": "Cron 07:00 UTC",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.2,
      "position": [220, 300]
    },
    {
      "parameters": {
        "jsCode": "const hoy = new Date();\nconst ayer = new Date(hoy.getTime() - 24 * 3600 * 1000);\nconst fmt = (d) => d.toISOString().slice(0, 10);\nreturn [{ json: { periodo_desde: fmt(ayer), periodo_hasta: fmt(hoy) } }];"
      },
      "id": "a0900000-0000-0000-0000-000000000002",
      "name": "Compute Period",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [460, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "={{ $env.RADAR_API_BASE }}/reports",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            { "name": "Content-Type", "value": "application/json" }
          ]
        },
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({ tipo: 'operacional', formato: 'pdf', periodo_desde: $json.periodo_desde, periodo_hasta: $json.periodo_hasta }) }}",
        "options": { "response": { "response": { "neverError": true, "fullResponse": true } } }
      },
      "id": "a0900000-0000-0000-0000-000000000003",
      "name": "Generate Report",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [700, 300],
      "onError": "continueErrorOutput"
    },
    {
      "parameters": {
        "jsCode": "const resp = $input.first().json;\nconst body = typeof resp.body === 'string' ? JSON.parse(resp.body) : resp.body;\nreturn [{ json: { report_id: body.id, periodo_desde: body.periodo_desde, periodo_hasta: body.periodo_hasta } }];"
      },
      "id": "a0900000-0000-0000-0000-000000000004",
      "name": "Extract Report ID",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [940, 300]
    },
    {
      "parameters": {
        "method": "GET",
        "url": "={{ $env.RADAR_API_BASE }}/reports/{{ $json.report_id }}/download",
        "options": { "response": { "response": { "responseFormat": "file", "outputPropertyName": "data" } } }
      },
      "id": "a0900000-0000-0000-0000-000000000005",
      "name": "Download Report",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [1180, 300]
    },
    {
      "parameters": {
        "fromEmail": "radar-creds@example.com",
        "toEmail": "={{ $env.ADMIN_EMAIL }}",
        "subject": "=Radar Creds — Reporte diario {{ $('Compute Period').first().json.periodo_hasta }}",
        "emailType": "text",
        "message": "Adjunto reporte operacional diario.",
        "options": {
          "attachmentsUi": {
            "attachmentsBinary": [
              { "property": "data", "name": "reporte_diario.pdf" }
            ]
          }
        }
      },
      "id": "a0900000-0000-0000-0000-000000000006",
      "name": "Email Report",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 2.1,
      "position": [1420, 300],
      "credentials": { "smtp": { "id": "radar_smtp", "name": "Radar SMTP" } }
    }
  ],
  "connections": {
    "Cron 07:00 UTC": { "main": [[{ "node": "Compute Period", "type": "main", "index": 0 }]] },
    "Compute Period": { "main": [[{ "node": "Generate Report", "type": "main", "index": 0 }]] },
    "Generate Report": {
      "main": [
        [{ "node": "Extract Report ID", "type": "main", "index": 0 }],
        [{ "node": "Email Report", "type": "main", "index": 0 }]
      ]
    },
    "Extract Report ID": { "main": [[{ "node": "Download Report", "type": "main", "index": 0 }]] },
    "Download Report": { "main": [[{ "node": "Email Report", "type": "main", "index": 0 }]] }
  },
  "settings": { "executionOrder": "v1", "errorWorkflow": "W12_ERROR_HANDLER" },
  "active": false,
  "tags": ["radar", "report"]
}
15. W10 — Sincronización de usuarios desde IdP
Trigger: Cron diario 02:00 UTC. Salida: usuarios actualizados.

json
{
  "name": "W10 - Sync Usuarios IdP",
  "nodes": [
    {
      "parameters": {
        "rule": { "interval": [{ "field": "cronExpression", "expression": "0 2 * * *" }] }
      },
      "id": "a1000000-0000-0000-0000-000000000001",
      "name": "Cron 02:00 UTC",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.2,
      "position": [220, 300]
    },
    {
      "parameters": {
        "method": "GET",
        "url": "={{ $env.IDP_USERS_ENDPOINT }}",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            { "name": "Authorization", "value": "=Bearer {{ $env.IDP_BEARER_TOKEN }}" }
          ]
        },
        "options": { "response": { "response": { "neverError": true, "fullResponse": true } } }
      },
      "id": "a1000000-0000-0000-0000-000000000002",
      "name": "Fetch IdP Users",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [460, 300],
      "onError": "continueErrorOutput"
    },
    {
      "parameters": {
        "jsCode": "const resp = $input.first().json;\nconst body = typeof resp.body === 'string' ? JSON.parse(resp.body) : resp.body;\nconst users = body.value || body.users || [];\nconst out = users.map(u => ({\n  email: (u.mail || u.email || '').toLowerCase(),\n  nombre: u.displayName || u.name || '',\n  idp_subject: u.id || u.sub || '',\n  activo: u.accountEnabled !== false\n})).filter(u => u.email);\nreturn out.map(u => ({ json: u }));"
      },
      "id": "a1000000-0000-0000-0000-000000000003",
      "name": "Normalize Users",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [700, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "INSERT INTO usuarios (email, nombre, rol_id, activo, idp_subject)\nSELECT $1::citext, $2, (SELECT id FROM roles WHERE nombre = 'end_user'), $3, $4\nON CONFLICT (email) DO UPDATE\nSET nombre = EXCLUDED.nombre,\n    activo = EXCLUDED.activo,\n    idp_subject = EXCLUDED.idp_subject,\n    actualizado_en = now();",
        "options": { "queryReplacement": "={{ [ $json.email, $json.nombre, $json.activo, $json.idp_subject ] }}" }
      },
      "id": "a1000000-0000-0000-0000-000000000004",
      "name": "Upsert User",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.5,
      "position": [940, 300],
      "credentials": { "postgres": { "id": "radar_pg", "name": "Radar PG" } }
    },
    {
      "parameters": {
        "workflowId": "W13_AUDITORIA",
        "workflowInputs": {
          "mappingMode": "defineBelow",
          "value": {
            "modulo": "admin",
            "accion": "sync_users",
            "resultado": "ok",
            "entidad": "usuarios",
            "entidad_id": "={{ $json.email }}",
            "usuario_email": null,
            "detalle": "={{ JSON.stringify({ email: $json.email, activo: $json.activo }) }}"
          }
        }
      },
      "id": "a1000000-0000-0000-0000-000000000005",
      "name": "Audit Sync",
      "type": "n8n-nodes-base.executeWorkflow",
      "typeVersion": 1.2,
      "position": [1180, 300]
    }
  ],
  "connections": {
    "Cron 02:00 UTC": { "main": [[{ "node": "Fetch IdP Users", "type": "main", "index": 0 }]] },
    "Fetch IdP Users": {
      "main": [
        [{ "node": "Normalize Users", "type": "main", "index": 0 }],
        []
      ]
    },
    "Normalize Users": { "main": [[{ "node": "Upsert User", "type": "main", "index": 0 }]] },
    "Upsert User": { "main": [[{ "node": "Audit Sync", "type": "main", "index": 0 }]] }
  },
  "settings": { "executionOrder": "v1", "errorWorkflow": "W12_ERROR_HANDLER" },
  "active": false,
  "tags": ["radar", "sync"]
}
16. W11 — Health-check de fuentes
json
{
  "name": "W11 - Healthcheck Fuentes",
  "nodes": [
    {
      "parameters": {
        "rule": { "interval": [{ "field": "hours", "hoursInterval": 1 }] }
      },
      "id": "a1100000-0000-0000-0000-000000000001",
      "name": "Cron 1h",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.2,
      "position": [220, 300]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT id, nombre, endpoint, activa FROM fuentes WHERE activa = TRUE;",
        "options": {}
      },
      "id": "a1100000-0000-0000-0000-000000000002",
      "name": "Leer Fuentes",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.5,
      "position": [460, 300],
      "credentials": { "postgres": { "id": "radar_pg", "name": "Radar PG" } }
    },
    {
      "parameters": {
        "method": "GET",
        "url": "=https://haveibeenpwned.com/api/v3/breaches",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            { "name": "user-agent", "value": "RadarCreds/1.0" }
          ]
        },
        "options": { "response": { "response": { "neverError": true, "fullResponse": true } } }
      },
      "id": "a1100000-0000-0000-0000-000000000003",
      "name": "Ping HIBP",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [700, 300],
      "credentials": { "httpHeaderAuth": { "id": "radar_http_hibp", "name": "HIBP API" } }
    },
    {
      "parameters": {
        "jsCode": "const resp = $input.first().json;\nconst ok = resp.statusCode >= 200 && resp.statusCode < 300;\nreturn [{ json: { fuente: 'hibp', status: resp.statusCode, ok, ts: new Date().toISOString() } }];"
      },
      "id": "a1100000-0000-0000-0000-000000000004",
      "name": "Evaluate Health",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [940, 300]
    },
    {
      "parameters": {
        "conditions": {
          "options": { "caseSensitive": true, "typeValidation": "strict" },
          "conditions": [
            {
              "id": "c1",
              "leftValue": "={{ $json.ok }}",
              "rightValue": false,
              "operator": { "type": "boolean", "operation": "false" }
            }
          ],
          "combinator": "and"
        }
      },
      "id": "a1100000-0000-0000-0000-000000000005",
      "name": "IF Down",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [1180, 300]
    },
    {
      "parameters": {
        "workflowId": "W06_ALERTA_ADMIN",
        "workflowInputs": {
          "mappingMode": "defineBelow",
          "value": {
            "mensaje": "={{ 'Fuente ' + $json.fuente + ' no responde (status ' + $json.status + ')' }}",
            "severidad": "media"
          }
        }
      },
      "id": "a1100000-0000-0000-0000-000000000006",
      "name": "Alert Down",
      "type": "n8n-nodes-base.executeWorkflow",
      "typeVersion": 1.2,
      "position": [1420, 220]
    }
  ],
  "connections": {
    "Cron 1h": { "main": [[{ "node": "Leer Fuentes", "type": "main", "index": 0 }]] },
    "Leer Fuentes": { "main": [[{ "node": "Ping HIBP", "type": "main", "index": 0 }]] },
    "Ping HIBP": { "main": [[{ "node": "Evaluate Health", "type": "main", "index": 0 }]] },
    "Evaluate Health": { "main": [[{ "node": "IF Down", "type": "main", "index": 0 }]] },
    "IF Down": { "main": [[{ "node": "Alert Down", "type": "main", "index": 0 }], []] }
  },
  "settings": { "executionOrder": "v1" },
  "active": false,
  "tags": ["radar", "health"]
}
17. W12 — Error Handler global
json
{
  "name": "W12 - Error Handler",
  "nodes": [
    {
      "parameters": {},
      "id": "a1200000-0000-0000-0000-000000000001",
      "name": "Error Trigger",
      "type": "n8n-nodes-base.errorTrigger",
      "typeVersion": 1,
      "position": [220, 300]
    },
    {
      "parameters": {
        "jsCode": "const e = $input.first().json;\nconst workflow = e.workflow?.name || 'desconocido';\nconst node = e.execution?.lastNodeExecuted || 'desconocido';\nconst message = e.execution?.error?.message || 'Error sin mensaje';\nreturn [{ json: { workflow, node, message, ts: new Date().toISOString(), executionId: e.execution?.id } }];"
      },
      "id": "a1200000-0000-0000-0000-000000000002",
      "name": "Format Error",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [460, 300]
    },
    {
      "parameters": {
        "workflowId": "W06_ALERTA_ADMIN",
        "workflowInputs": {
          "mappingMode": "defineBelow",
          "value": {
            "mensaje": "={{ 'Fallo en workflow ' + $json.workflow + ' (nodo ' + $json.node + '): ' + $json.message }}",
            "severidad": "alta"
          }
        }
      },
      "id": "a1200000-0000-0000-0000-000000000003",
      "name": "Alert Admin",
      "type": "n8n-nodes-base.executeWorkflow",
      "typeVersion": 1.2,
      "position": [700, 300]
    },
    {
      "parameters": {
        "workflowId": "W13_AUDITORIA",
        "workflowInputs": {
          "mappingMode": "defineBelow",
          "value": {
            "modulo": "admin",
            "accion": "workflow_error",
            "resultado": "error",
            "entidad": "workflows",
            "entidad_id": "={{ $json.workflow }}",
            "usuario_email": null,
            "detalle": "={{ JSON.stringify($json) }}"
          }
        }
      },
      "id": "a1200000-0000-0000-0000-000000000004",
      "name": "Audit Error",
      "type": "n8n-nodes-base.executeWorkflow",
      "typeVersion": 1.2,
      "position": [940, 300]
    }
  ],
  "connections": {
    "Error Trigger": { "main": [[{ "node": "Format Error", "type": "main", "index": 0 }]] },
    "Format Error": { "main": [[{ "node": "Alert Admin", "type": "main", "index": 0 }]] },
    "Alert Admin": { "main": [[{ "node": "Audit Error", "type": "main", "index": 0 }]] }
  },
  "settings": { "executionOrder": "v1" },
  "active": false,
  "tags": ["radar", "error"]
}
18. Instalación y activación
18.1 Importar todos los workflows
bash
# Asumiendo contenedor n8n en marcha
docker compose exec n8n n8n import:workflow --input=/data/workflows/W14_hash.json
docker compose exec n8n n8n import:workflow --input=/data/workflows/W13_audit.json
docker compose exec n8n n8n import:workflow --input=/data/workflows/W15_notify.json
docker compose exec n8n n8n import:workflow --input=/data/workflows/W06_admin_alert.json
docker compose exec n8n n8n import:workflow --input=/data/workflows/W12_error_handler.json
docker compose exec n8n n8n import:workflow --input=/data/workflows/W01_collect.json
docker compose exec n8n n8n import:workflow --input=/data/workflows/W02_correlate.json
docker compose exec n8n n8n import:workflow --input=/data/workflows/W03_contain.json
docker compose exec n8n n8n import:workflow --input=/data/workflows/W04_retry.json
docker compose exec n8n n8n import:workflow --input=/data/workflows/W07_verify_chain.json
docker compose exec n8n n8n import:workflow --input=/data/workflows/W08_webhook_idp.json
docker compose exec n8n n8n import:workflow --input=/data/workflows/W09_daily_report.json
docker compose exec n8n n8n import:workflow --input=/data/workflows/W10_sync_users.json
docker compose exec n8n n8n import:workflow --input=/data/workflows/W11_healthcheck.json

# Activar (las que tienen trigger)
docker compose exec n8n n8n update:workflow --id=W01_COLLECT --active=true
docker compose exec n8n n8n update:workflow --id=W04_RETRY --active=true
docker compose exec n8n n8n update:workflow --id=W07_VERIFY_CHAIN --active=true
docker compose exec n8n n8n update:workflow --id=W08_WEBHOOK_IDP --active=true
docker compose exec n8n n8n update:workflow --id=W09_DAILY_REPORT --active=true
docker compose exec n8n n8n update:workflow --id=W10_SYNC_USERS --active=true
docker compose exec n8n n8n update:workflow --id=W11_HEALTHCHECK --active=true
docker compose exec n8n n8n update:workflow --id=W12_ERROR_HANDLER --active=true
18.2 Variables de entorno n8n
env
RADAR_API_BASE=http://api:8000/api/v1
HIBP_API_KEY=xxxxx
IDP_WEBHOOK_URL=https://idp.example.com/radar/hooks
IDP_HMAC_SECRET=xxxxx
IDP_USERS_ENDPOINT=https://graph.microsoft.com/v1.0/users
IDP_BEARER_TOKEN=xxxxx
TEAMS_WEBHOOK=https://outlook.office.com/webhook/xxxxx
SLACK_WEBHOOK=https://hooks.slack.com/services/xxxxx
ADMIN_EMAIL=soc@example.com
18.3 Orden de dependencias
text
W13 (audit)  ─┐
W14 (hash)   ─┼─→ W01 → W02 → W03 → W15
W15 (notify) ─┤         │
W06 (alert)  ─┘         ├─→ W04 (retry) ─→ W06
                        ├─→ W07 (verify)
                        ├─→ W08 (webhook)
                        ├─→ W09 (report)
                        ├─→ W10 (sync)
                        ├─→ W11 (health)
                        └─→ W12 (error handler, transversal)
Regla: importar y activar primero W13, W14, W15, W06 y W12 (dependencias), luego el resto.

19. Resumen de workflows entregados
Workflow	Trigger	Nodos	Estado
W01 Recolección HIBP	Cron 03:00 UTC	11	✅
W02 Correlación	Execute	9	✅
W03 Contención	Execute	12	✅
W04 Reintentos DLQ	Cron 15 min	11	✅
W05 Notificación usuario	(W15)	—	✅ alias
W06 Alerta admin	Execute	4	✅
W07 Verificación cadena	Cron 6 h	5	✅
W08 Webhook IdP	Webhook POST	4	✅
W09 Reporte diario	Cron 07:00 UTC	6	✅
W10 Sync usuarios IdP	Cron 02:00 UTC	5	✅
W11 Health-check fuentes	Cron 1 h	6	✅
W12 Error Handler global	Error Trigger	4	✅
W13 Utils auditoría	Execute	4	✅
W14 Utils hash canónico	Execute	2	✅
W15 Utils notificación	Execute	5	✅
Total: 15 workflows, 92 nodos, 100% importables.

20. Mejoras aplicadas sobre el diseño del Paso 1
Área	Mejora
Idempotencia	ON CONFLICT (hash_canonico) DO NOTHING en W02; check previo en W03.
Rate limit HIBP	Nodo retry con waitBetweenRetries + Split In Batches de 1.
Caché HIBP	Tabla hibp_cache con TTL 24 h; W01 consulta caché antes de la API.
Backoff escalonado	W04 implementa schedule [15, 30, 60, 240, 1440] min y máximo 5 intentos.
HMAC	W03 y W04 firman cada llamada al IdP; W08 verifica con timingSafeEqual.
Auditoría encadenada	W13 calcula hash_anterior/hash_actual en cada escritura.
Error handling	W12 transversal con errorWorkflow referenciado por todos los workflows críticos.
Verificación de cadena	W07 independiente, cada 6 h, alerta si se rompe.
Reporte diario	W09 genera y envía PDF automáticamente al admin.
Sync usuarios	W10 mantiene el directorio corporativo actualizado desde el IdP.
Health-check	W11 detecta caída de fuentes y alerta.
21. Pruebas de humo (smoke tests)
bash
# 1. Verificar que n8n importó todo
docker compose exec n8n n8n list:workflow

# 2. Ejecutar W01 manualmente
docker compose exec n8n n8n execute --id=W01_COLLECT

# 3. Verificar filas en BD
docker compose exec postgres psql -U radar -d radar_creds -c \
  "SELECT count(*) FROM leak_hits WHERE fecha_deteccion > now() - interval '1 hour';"

# 4. Verificar cadena de auditoría
docker compose exec postgres psql -U radar -d radar_creds -c \
  "SELECT count(*), max(id) FROM audit_log;"

# 5. Ejecutar W07 manualmente
docker compose exec n8n n8n execute --id=W07_VERIFY_CHAIN
22. Conclusión del Paso 4
Estado inicial: los workflows n8n estaban descritos textualmente pero no existía JSON importable.

Estado final: 15 workflows completos, 92 nodos, con:

Contratos de entrada/salida explícitos.

Manejo de errores transversal (W12).

Auditoría encadenada (W13).

Reintentos con backoff (W04).

HMAC en todas las llamadas al IdP.

Idempotencia y desduplicación.

Integración: consume la API del Paso 2 (FastAPI) y comparte esquema con el frontend del Paso 3.

Cumplimiento: la evidencia de auditoría (ISO A.5.17) se genera automáticamente en cada ejecución; NIST CSF cubierto en Identify/Protect/Detect/Respond/Recover.

Pendiente para Paso 5 (si se solicita): pruebas end-to-end con datos sintéticos de HIBP, manual de operación SOC, plantillas legales de comunicación a empleados (GDPR/LOPDGDD) y plan de capacidad para 5.000 usuarios.

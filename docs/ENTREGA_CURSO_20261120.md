# Entrega del Caso24

Actualización del 20 de noviembre de 2026, hora de Lima. El software se modificó en el directorio original indicado por el usuario. El manuscrito anterior se conserva sin sobrescribir.

## Resultado principal

Se ejecutó un experimento nuevo sobre 10 000 observaciones derivadas del benchmark público sintético [PWLDS de Infinitode](https://github.com/Infinitode/PWLDS/tree/c16f18d080e41b54da727445d0505f2c74d53f6a), con licencia CC BY 4.0 y atribución incluida. No se descargó un corpus de credenciales robadas. Se mapearon cinco niveles sintéticos a tres clases de debilidad.

| Modelo | Macro F1 validación | Macro F1 prueba |
| --- | ---: | ---: |
| M1 Regresión logística | 92,60 % | 88,43 % |
| M2 Random Forest | 95,55 % | 93,83 % |
| M3 Boosting por histogramas | 95,17 % | 94,94 % |

M2 fue elegido por validación antes de abrir la prueba. M3 no se eligió retrospectivamente usando la prueba. Las predicciones de los tres modelos se reprodujeron exactamente a partir de los arrays y las particiones conservadas. Los intervalos exploratorios se superponen; no se afirma superioridad estadística.

El dataset sirve para comparación controlada de debilidad. No acredita eficacia frente a ataques, exposición de correos ni toma de cuentas. El modelo puede consultarse en previsualización, pero su activación para contenciones está bloqueada por ser sintético. El motor operativo mantiene las reglas si no hay un artefacto autorizado activo.

## Qué se entrega

- `Articulo_Radar_Caso24_Entrenamiento_Actualizado.docx`: artículo en español con resumen inglés, metodología detallada, cuatro figuras, siete tablas, resultados actuales, discusión y referencias.
- `Evidencias_Caso24_20261120.zip`: datos derivados y licencia, los tres modelos, particiones, predicciones, hashes, instantánea del código de entrenamiento, reproducción verificada, JTL de JMeter, JMX, resúmenes y metadatos depurados de n8n.
- `Motor_entrenamiento_Caso24.md`: diagnóstico, protocolo, fichas y guía del motor, actualizada respecto a vectores ambiguos.

## Acceso al laboratorio

- Frontend: http://127.0.0.1:5173/training
- API y documentación: http://127.0.0.1:8000/docs
- n8n: http://localhost:5678/
- Mailpit local: http://127.0.0.1:8025/

La cuenta Owner de n8n es independiente de los usuarios de la aplicación. Se utilizó la cuenta corregida proporcionada en el chat y no se guarda su contraseña en esta entrega. El frontend conserva su autenticación: utiliza las credenciales existentes de la aplicación; no se sustituyó su contraseña con la de n8n.

La ejecución científica disponible en el registro es `90709911-241e-4104-988d-40102c02be1c`, con dataset `2ee02b1e-9e87-45b6-82fa-d331abd23049`. En el panel, Datos y EDA muestra procedencia y calidad; Comparación presenta las matrices y métricas; Registro distingue el ganador de investigación del modelo activo.

Los 15 workflows del radar permanecen sin publicar/activar para ejecución programada. Se verificaron manualmente con fixtures; las automatizaciones ajenas al radar se conservaron. El workflow adicional `Radar Curso - Verificación manual controlada` queda apuntando al cálculo inocuo de hash W14. Las notificaciones de prueba fueron a Mailpit y servicios locales.

## Resultados operacionales medidos

JMeter 5.6.3 generó 7277 solicitudes válidas sin errores HTTP. Se midieron cinco operaciones por bucle, incluida inferencia de M2, con pausa de 100 ms y perfiles de 20 s.

| Usuarios | Solicitudes | Solicitudes/s | p95 global | p95 inferencia M2 |
| ---: | ---: | ---: | ---: | ---: |
| 5 | 875 | 44,23 | 14 ms | 19 ms |
| 15 | 2545 | 128,50 | 23 ms | 30,85 ms |
| 25 | 3857 | 194,53 | 55 ms | 75,90 ms |

Es una prueba local breve con un trabajador de API, sin entrenamiento concurrente. No mide capacidad máxima ni latencia de contención de n8n. El inicio de sesión se excluyó de la medición y las consultas usaron un token temporal de auditor desactivado después del experimento.

Se corrigieron y comprobaron referencias de subflujos, el procesamiento positivo de reintentos W04 y HMAC sobre el cuerpo original en W08. W08 aceptó una firma válida y rechazó una inválida con HTTP 401. W12 se verificó con un error inyectado y se restauró su disparador original: el disparo automático ante un error real no queda acreditado por esa prueba. Las ramas de agotamiento, fallos permanentes y caída de servicios externos siguen pendientes de validación adicional.

El backend pasó 34 pruebas contra una base temporal separada. El frontend tuvo 12 pruebas satisfactorias; la construcción final se verificó después de mostrar los vectores ambiguos. Los avisos de lint preexistentes no se interpretan como errores de compilación.

## Reinicio local

Desde la raíz original del proyecto, con Docker disponible y las configuraciones privadas existentes:

```bash
cd backend
docker compose up -d postgres redis
cd ../n8n
docker compose -f docker-compose.n8n.yml up -d
cd ..
backend/.venv/bin/python scripts/start_course_lab.py
```

En otra terminal:

```bash
cd frontend
npm run dev -- --host 127.0.0.1
```

El supervisor usa `backend/.env` y `n8n/.env` sin copiarlos a reportes, dirige las salidas a fixtures y guarda registros privados en `backend/runtime/course_lab`. No dupliques el supervisor si 8000 y 9000 ya están ocupados. No actives workflows de producción para repetir esta demostración.

## Cómo reproducir las cifras

Extrae el ZIP en un directorio de evidencias y consulta su `README.md`. El script `scripts/replay_experiment.py` vuelve a ejecutar la búsqueda de tres candidatos por modelo sobre los folds archivados y comprueba la coincidencia exacta de todas las predicciones de prueba y de los artefactos. Esta comprobación ya se ejecutó y su salida está incluida en `training/replay_result.json`.

Una nueva importación del CSV crea huellas de grupo con sal distinta y puede producir otra partición aleatoria. Para repetir exactamente el artículo hay que conservar `features.npz` y `partition.npz`, no asumir que volver a importar recrea los mismos índices.

## Revisión antes de remitir

La redacción actualiza la metodología y las conclusiones con las mediciones conservadas. Los resultados históricos del artículo anterior no se presentan como resultados nuevos ni como un antes y después comparable con este experimento.

Los autores deben revisar el contenido y completar, según corresponda, correo formal de correspondencia, contribuciones, financiación y conflictos de interés. No se ha afirmado su aprobación de esta versión. La declaración de asistencia de Codex está incluida.

No se seleccionó ni verificó una revista ni se asignó un cuartil a este manuscrito. Su nombre ya no afirma Q1 o Q3 sin evidencia. Tampoco se ha enviado a Turnitin o a terceros, ni se garantiza un porcentaje de similitud. Para una futura revista se deberán verificar sus normas, indexación, categoría y cuartil del año pertinente, y adaptar el formato editorial.

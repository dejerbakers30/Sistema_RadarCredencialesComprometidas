# Motor de entrenamiento del Radar de Credenciales Comprometidas

El laboratorio integra entrenamiento, comparación y registro de tres clasificadores de **debilidad de contraseñas** en el Radar del Caso 24. El modelo ganador se elige mediante validación y se conserva sin reajustar para que la inferencia cargue exactamente el artefacto evaluado. La evaluación científica del caso requiere un dataset autorizado, etiquetas defendibles y validación independiente; las pruebas sintéticas incluidas verifican funcionamiento.

## Diagnóstico del sistema anterior

El radar detecta exposiciones mediante HIBP y correlación determinista, orquesta operaciones con n8n y conserva los registros operacionales y la auditoría en PostgreSQL. HIBP describe las categorías de información de una filtración mediante `DataClasses`; la consulta de una cuenta no proporciona su contraseña. Véase la [API oficial de HIBP](https://haveibeenpwned.com/API/v3).

Antes del cambio, `risk_engine.py` entrenaba una regresión logística al importar el módulo, con ejemplos manuales de tres clases. `evaluate_model.py` entrenaba un Random Forest diferente, con etiquetas binarias generadas mediante longitud y pertenencia a una lista. Ese experimento no evaluaba el modelo utilizado en la aplicación. El archivo RockYou citado por el script no estaba disponible durante esta implementación. Las métricas históricas no se reinterpretan como resultados del laboratorio actual.

Además, la contención trataba una contraseña candidata clasificada como de riesgo bajo como motivo para omitir la respuesta y marcar una exposición como falso positivo. Ese vínculo se eliminó: la debilidad estimada se conserva como dato auxiliar y no invalida una exposición confirmada. Los falsos positivos deben determinarse mediante evidencia sobre la exposición.

## Tarea y alcance de la IA

| Elemento | Definición |
| --- | --- |
| Unidad de análisis | Una observación de características de una contraseña, asociada a una familia opaca |
| Población objetivo | La población representada por el dataset autorizado; no se presupone generalización universal |
| Objetivo | Reproducir la clasificación de debilidad definida por el protocolo de etiquetado |
| Clases | Bajo, Medio y Crítico, referidas exclusivamente a debilidad estimada |
| Entradas | Ocho características numéricas disponibles durante inferencia |
| Utilidad | Evaluación auxiliar de debilidad, comparación de algoritmos y evidencia experimental |
| Fuera del alcance | Detectar filtraciones, estimar probabilidad de toma de cuentas o decidir omitir contención |

Si las etiquetas son heurísticas, las métricas miden concordancia con esas reglas. Cuando la etiqueta se deriva de una variable de entrada, un rendimiento elevado puede reflejar circularidad. Las reglas explícitas y la clase mayoritaria se incluyen como referencias. No se atribuyen estos umbrales a NIST ni se certifica cumplimiento normativo.

## Flujo metodológico

```mermaid
flowchart LR
  A[Fuente autorizada y procedencia] --> B[Validación de esquema y EDA]
  B --> C[Familias y duplicados]
  C --> D[Partición por grupos 70 15 15]
  D --> E[CV interna del entrenamiento]
  E --> F[Búsqueda M1 M2 M3]
  F --> G[Ajuste con entrenamiento]
  G --> H[Selección por validación]
  H --> I[Congelar modelo ganador]
  I --> J[Abrir prueba final]
  J --> K[Artefactos y evidencia]
  K --> L[Activación administrativa]
  L --> M[Inferencia auxiliar]
```

La validación de esquema rechaza valores ausentes, infinitos y fuera de rango. No se imputa información silenciosamente. El único transformador aprendido es `StandardScaler` en M1, ajustado dentro de cada fold mediante un pipeline. La normalización de grupos y la identificación de vectores iguales no utilizan la etiqueta para aprender predictores. Sí se consulta la distribución de clases para construir particiones viables y estratificadas.

## Datos y procedencia

La API acepta CSV UTF-8 con esta cabecera exacta y en este orden:

```csv
length,entropy,digits_ratio,uppercase_ratio,symbols_ratio,common_pattern,only_letters_or_digits,num_symbols,label,group_id
```

Las características corresponden a `extract_features` sin recortar espacios ni cambiar mayúsculas del valor original. `length` es la longitud en caracteres; `entropy` es la entropía de Shannon empírica por carácter, que no equivale a resistencia a adivinación; las razones representan dígitos, mayúsculas y símbolos. `common_pattern` y `only_letters_or_digits` son indicadores binarios. `num_symbols` cuenta caracteres no alfanuméricos. El esquema vigente es `password-features-v1`.

Se requieren 90–20000 filas, máximo 3 MB, las tres clases con al menos veinte observaciones y diez grupos efectivos por clase. Longitud admitida: 1–256. Se comprueba coherencia entre proporción y cantidad de símbolos. Estos mínimos son controles operativos; no constituyen un cálculo de potencia ni garantizan viabilidad científica.

`group_id` identifica una familia de observaciones relacionadas y debe ser opaco, con letras ASCII, números, guiones o guiones bajos. No se aceptan correos como grupo. El proveedor debe agrupar variantes relacionadas antes de importar. El motor une adicionalmente grupos que comparten vectores idénticos y conserva vectores iguales con etiquetas distintas, registrando su ambigüedad. Distintas cadenas pueden compartir las ocho características; descartarlas sesgaría la evaluación. No identifica todas las similitudes semánticas.

Los identificadores originales se sustituyen por HMAC con una clave aleatoria por importación que no se conserva. El CSV original no se guarda; se registra su SHA-256 y se guardan arrays numéricos, clases y grupos transformados. Las características aún pueden ser sensibles: el almacenamiento no es un conjunto público anonimizado y requiere control de acceso y protección del disco.

La procedencia contiene fuente y versión, licencia o autorización, procedimiento de etiquetado, tipo de evidencia y confirmación de autorización:

```json
{
  "source": "Identificador de la colección y su versión",
  "license": "Condiciones de uso verificadas por el responsable",
  "label_method": "Descripción del procedimiento de etiquetado y sus limitaciones",
  "kind": "heuristic",
  "authorized": true
}
```

`kind` admite `synthetic`, `heuristic` y `expert`. Declarar `expert` no verifica automáticamente la calidad del etiquetado. Antes de investigación se necesita documentar responsables, criterios, desacuerdos, revisión y representatividad. Los modelos de datasets sintéticos no pueden activarse mediante la API.

## Partición y validación

Se buscan particiones por grupos cercanas a 70 % entrenamiento, 15 % validación y 15 % prueba. Entre 120 candidatos deterministas se elige uno por proximidad de tamaños y distribución de clases; no se utilizan resultados de los modelos para elegirlo. Se conservan grupos completos y se exige presencia de las tres clases en cada conjunto y fold. Los tamaños efectivos quedan registrados; pueden diferir de 70/15/15.

Sobre el entrenamiento se construye `StratifiedGroupKFold`, por defecto con tres folds y semilla 42. Los índices completos de conjuntos y folds se guardan en `partition.npz`. La [documentación de scikit-learn sobre fugas de información](https://scikit-learn.org/stable/common_pitfalls.html) explica por qué el preprocesamiento aprendido debe permanecer dentro del entrenamiento.

Esta tarea es transversal, no un pronóstico de eventos futuros. Si se cambia a priorización temporal de exposiciones será necesario otro esquema de variables, etiquetas, partición cronológica y evaluación. No se aplica automáticamente este clasificador a una tarea diferente.

La búsqueda usa solo CV dentro del 70 %. Cada modelo elegido por CV se ajusta con ese entrenamiento. El 15 % de validación selecciona el ganador por macro F1, con desempate M1, M2, M3. Se guarda `frozen_at` antes de abrir prueba y `test_opened_at` antes de producir sus métricas. Se evalúan los tres candidatos para comparación final, sin cambiar el ganador después de ver prueba. No se reajusta con validación, de modo que el artefacto activado conserva la evaluación final.

Un conjunto cuyo resultado ya se examinó para modificar el sistema deja de ser una prueba independiente de esos cambios. El registro avisa si la misma fuente, identificada por el hash del CSV, ya tuvo aperturas de prueba. Esto no detecta todas las reexportaciones o versiones del mismo corpus. El responsable debe reservar una colección independiente para confirmar generalización.

## Parametrización de los tres modelos

Los siguientes son valores iniciales propuestos, no óptimos demostrados. La interfaz permite modificarlos dentro de límites. El primer ensayo usa esa configuración; los siguientes muestrean sin reemplazo el espacio discreto con la misma semilla. La búsqueda aleatoria acotada evita incorporar otro servicio o dependencia de optimización para solo ocho variables y tres algoritmos. No utiliza Optuna ni anuncia poda inexistente.

| Modelo | Configuración inicial | Valores explorados | Parada |
| --- | --- | --- | --- |
| M1 Regresión logística | C 1, max_iter 500, tol 0.0001; lbfgs; class_weight balanced; StandardScaler | C 0.01, 0.1, 1, 10; tol 0.0001, 0.001 | Convergencia o max_iter; se descartan ensayos sin convergencia |
| M2 Random Forest | 100 árboles, profundidad 12, mínimo 2 observaciones por hoja; max_features sqrt; class_weight balanced; un hilo | Árboles 50, 100, 200; profundidad 6, 12, 20; hojas 1, 2, 5 | Construcción de los árboles configurados; sin épocas ni early stopping |
| M3 Histogram Gradient Boosting | 100 iteraciones, learning_rate 0.1, 15 hojas máximas, L2 1; class_weight balanced | Iteraciones 50, 100, 200; tasa 0.03, 0.1, 0.2; hojas 7, 15, 31; L2 0, 1, 5 | max_iter; early_stopping desactivado para no introducir una partición interna aleatoria incompatible con grupos |

Presupuesto por defecto: tres ensayos por modelo, tres folds, 600 segundos y un hilo de cómputo nativo. Se permiten 1–8 ensayos, 2–5 folds y 30–1800 segundos. Cancelación y presupuesto se comprueban entre ajustes y etapas: no se promete interrupción inmediata de un ajuste en curso. No hay entrenamiento incremental ni reanudación de un ensayo parcial; una nueva ejecución conserva el historial anterior.

## Métricas e interpretación

La selección utiliza macro F1 para dar peso equivalente a cada clase. Se registran matriz de confusión, precision, recall, F1 y soporte por clase, balanced accuracy, PR-AUC y ROC-AUC macro one-vs-rest, Brier multiclase y log loss. Las probabilidades se usan internamente para estas métricas; no se presentan como probabilidades calibradas de ataque. El umbral implícito de decisión es el argmax del clasificador; no se ajustan umbrales usando prueba.

La incertidumbre exploratoria de macro F1 utiliza 200 remuestreos de grupos con reemplazo y percentiles 2.5 y 97.5. Debe revisarse la estabilidad con más grupos y un número mayor de remuestreos antes de publicación. No se ejecuta una prueba de superioridad estadística. Los folds dependientes no se tratan como observaciones independientes. Una comparación inferencial requiere un diseño específico sobre predicciones pareadas y grupos independientes.

También se conservan tiempo de entrenamiento por modelo, tamaño y hash del artefacto, y latencia media por fila de una predicción en lote. Esta última no es latencia de una petición HTTP ni rendimiento de producción.

Las métricas de detección HIBP, deduplicación, contención, n8n y auditoría siguen siendo experimentos operacionales separados en `experiments/`. No se combinan con macro F1 para afirmar una única precisión del radar.

## Arquitectura y persistencia

El backend conserva FastAPI y PostgreSQL. La API de laboratorio reutiliza permisos existentes: `reports:read` para consultar y exportar; `config:admin` para importar, entrenar, cancelar y activar. Las acciones API se registran en la cadena de auditoría PostgreSQL mediante el servicio existente, sin modificar su implementación ni las migraciones.

Los arrays, manifiestos JSON, particiones, predicciones y pipelines joblib se guardan en un directorio de artefactos privado. Por defecto es `backend/runtime/ml`; se puede configurar `RADAR_ML_STORAGE`. Este índice local no reemplaza PostgreSQL como base operacional. No ofrece transacciones distribuidas entre disco y PostgreSQL; se debe respaldar junto con la aplicación. El CLI local no tiene identidad web y registra `actor_id=local-cli`; su manifiesto local no equivale a la cadena inmutable PostgreSQL de las acciones API.

El modelo activo se representa mediante un puntero escrito atómicamente. Se comprueban estado completo, esquema, clases, dimensiones, versión de scikit-learn y hash del artefacto antes de cargarlo. Solo se cargan archivos locales generados por el motor; no se admiten modelos pickle/joblib subidos. La [documentación oficial de persistencia](https://scikit-learn.org/stable/model_persistence.html) advierte del riesgo de deserializar artefactos no confiables y de la falta de soporte para versiones diferentes.

Un proceso separado realiza el entrenamiento, con bloqueo `flock` heredado para impedir ejecuciones simultáneas incluso con varios procesos API en el mismo servidor. Si el trabajador muere, el bloqueo se libera y el registro se marca interrumpido al consultar. No es una cola distribuida; el despliegue debe usar almacenamiento local compartido por los procesos y un único host. Los artefactos y procesos deben conservar el mismo usuario del servicio. Para múltiples hosts se necesita una cola y registro coordinados adicionales.

El fallo de un entrenamiento no sustituye el modelo activo. Un artefacto ausente, incompatible o corrupto conduce a reglas conservadoras de debilidad. Se eliminó todo entrenamiento durante la importación o por petición. Las entradas vacías, inválidas o superiores a 256 caracteres retornan Crítico sin procesar un modelo. Para entradas admitidas, la inferencia usa `extract_features` y el mismo pipeline evaluado.

JDBC es una API de conectividad para Java; no representa un algoritmo ni exige tres gestores. No se migró a Java ni se añadieron SQL Server y Oracle.

## Uso desde la aplicación

1. Iniciar PostgreSQL, Redis y el backend con su configuración habitual. Usar `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000` desde `backend` con el entorno activo.
2. Iniciar el frontend con `npm run dev` y entrar con una cuenta que tenga `reports:read`.
3. Abrir **Análisis → Laboratorio IA** o `/training`.
4. Descargar la plantilla. Importar características y procedencia con una cuenta autorizada para `config:admin`.
5. Revisar EDA, clases y grupos; configurar modelos, semilla, folds y presupuesto.
6. Iniciar entrenamiento y consultar el historial. Las condiciones de parada y parámetros permanecen visibles.
7. Revisar comparación, limitaciones, matrices de confusión y exportar evidencia JSON.
8. Activar el ganador de una ejecución no sintética solo después de revisar su procedencia y limitaciones. El registro permite volver a reglas o activar otro ganador previo.

El icono de sol o luna del encabezado cambia el tema claro y oscuro y conserva la preferencia. La primera visita utiliza la preferencia del sistema.

## Uso desde consola

Desde `backend`, con el entorno activo y `RADAR_ML_STORAGE` apuntando a una ubicación privada:

```bash
python evaluate_model.py --csv /ruta/autorizada/caracteristicas.csv --provenance /ruta/autorizada/procedencia.json
```

Opcionalmente, `--config` acepta JSON compatible con `RunConfig`. El comando usa el mismo motor, particiones, métricas y verificación de artefactos que la API. No activa el modelo automáticamente ni genera etiquetas a partir de un corpus raw.

Cada ejecución conserva el hash de los datos, fuente y licencia, procedimiento de etiquetado, configuración, índices, semilla, folds, métricas, predicciones de prueba con índices y grupos transformados, versiones, plataforma, arquitectura de CPU, hilos, commit y hashes de los módulos del motor. El commit puede corresponder a un árbol con cambios locales; los hashes de código permiten identificar esos archivos. Las dependencias exactas medidas quedan en cada manifiesto.

## Verificación y pendientes

Pruebas del motor sin PostgreSQL, desde `backend`:

```bash
python -m pytest tests_ml -q
```

Las pruebas de integración requieren una **base PostgreSQL exclusiva de pruebas** en `TEST_DATABASE_URL`. El fixture existente aplica migraciones y revierte el esquema al finalizar: nunca apuntar esa variable a la base de trabajo.

```bash
python -m alembic upgrade head
python -m pytest app/tests tests_ml -q
```

Frontend:

```bash
npm run typecheck
npm run lint
npm test -- --run
npm run build
```

La implementación se verificó el 20 de noviembre de 2026 con 34 pruebas backend aprobadas en PostgreSQL 16 temporal, 12 pruebas frontend aprobadas, compilación de producción y revisión de escritorio, ambos temas y móvil a 390 píxeles. Hubo avisos de dependencias; no se tratan como errores de compilación. Se comprobaron autenticación, escritura restringida, bloqueo de entrenamiento, integridad, separación por grupos, cancelación, coincidencia de predicciones del artefacto y protección contra activación de datos sintéticos.

Los quince workflows n8n se verificaron en casos manuales o subflujos con fixtures locales. Se corrigieron referencias de subflujos, sincronización y recorrido de reintentos W04, y HMAC sobre bytes originales con rechazo HTTP 401 en W08. Permanecen inactivos para programación. W12 recibió un evento de error inyectado y se restauró su Error Trigger; no se acredita con ello su disparo automático. Las ramas de agotamiento, fallos permanentes y caída de integraciones externas requieren comprobaciones adicionales. No se realizaron contenciones sobre cuentas reales.

Se obtuvo y entrenó una muestra pública autorizada de PWLDS, descrita en la actualización siguiente. Para investigación permanecen pendientes etiquetas independientes y representativas del objetivo operativo, evaluación externa, una justificación de tamaño basada en ese objetivo y comparaciones inferenciales apropiadas. El artículo se actualizó por la solicitud posterior del usuario; la selección y adaptación a una revista no se efectuó. Ningún resultado sintético permite afirmar eficacia operacional, indexación, aceptación editorial o un porcentaje de Turnitin.


## Resultados de la actualización experimental

Se entrenaron los tres modelos sobre 10 000 observaciones derivadas de PWLDS de Infinitode, commit `c16f18d080e41b54da727445d0505f2c74d53f6a`, licencia CC BY 4.0. Se muestrearon 2000 filas por clase original dentro de los primeros 50 000 registros de cada archivo, con semilla reservoir 20261120 más clase. Las cinco clases de fortaleza se mapearon a tres niveles de debilidad. La fuente es sintética y sus etiquetas provienen de generación, no de ataques ni de expertos.

Se preservaron 113 vectores ambiguos, 6739 repeticiones de características y 3259 grupos consolidados. Los conjuntos efectivos fueron 7029 entrenamiento, 1354 validación y 1617 prueba. La sal del importador puede variar entre importaciones; para reproducción exacta se conservan arrays y particiones.

| Modelo | CV macro F1 | Validación macro F1 | Prueba macro F1 |
| --- | ---: | ---: | ---: |
| M1 | 88,47 % | 92,60 % | 88,43 % |
| M2 | 92,05 % | 95,55 % | 93,83 % |
| M3 | 92,27 % | 95,17 % | 94,94 % |

Ejecución `90709911-241e-4104-988d-40102c02be1c`, con tres candidatos por modelo, tres folds, semilla 42 y presupuesto 1200 s. M2 se seleccionó por validación antes de la prueba y permanece como ganador de investigación. Su IC exploratorio por grupos fue 85,85–96,66 %. La regla fija obtuvo macro F1 de 76,93 %. No se declara significación estadística ni mejoría frente a ataques. El artefacto sintético no está activo para contenciones.

La previsualización autorizada usa `POST /api/v1/training/runs/{id}/predict` con un objeto `features` de ocho valores finitos en el orden del esquema. Devuelve la clase, el modelo, el ID de ejecución y `preview=true`; no acepta una contraseña raw, no activa el modelo ni modifica contenciones. Este endpoint permitió medir con JMeter el mismo M2 persistido que se evaluó.

Los tres modelos se reajustaron y sus predicciones coincidieron exactamente con las archivadas. JMeter 5.6.3 registró 7277 peticiones válidas sin errores HTTP en perfiles locales de 5, 15 y 25 usuarios. Con 25 usuarios se midieron 194,53 solicitudes/s, p95 global 55 ms y p95 de previsualización 75,90 ms. Son perfiles de 20 s con pausa de 100 ms; no determinan capacidad máxima. Los resultados de integración, entrenamiento e inferencia se mantienen separados.

La guía de entrega y el ZIP de evidencias incluyen comandos portables, hashes, JTL, manifiestos y las restricciones para repetir cada evaluación. El supervisor `scripts/start_course_lab.py` conserva las configuraciones privadas y dirige IdP, HIBP y notificaciones a los servicios locales de demostración.

# Guía de Pruebas de Rendimiento con Apache JMeter 5.6.3
**Sistema:** Radar de Credenciales Comprometidas  
**Objetivo:** Determinar la capacidad máxima, el punto de saturación y la estabilidad bajo carga de la plataforma.

---

## 1. Justificación Arquitectónica: ¿API, Base de Datos o Ambas?

Una duda fundamental en ingeniería de software es si las pruebas de carga deben hacerse contra la API HTTP o directamente contra la Base de Datos (PostgreSQL en Docker).

### Conclusión Técnica y Metodológica:
Se aplica una **estrategia híbrida por capas (Top-Down)**:

1. **Prueba Principal (Obligatoria a Nivel de Sistema): API REST**
   - **Por qué:** En entornos reales, ni los analistas del SOC ni las interfaces web interactúan directamente con la base de datos por JDBC/TCP. Consumen endpoints REST autenticados mediante tokens JWT.
   - **Qué mide:** Mide el sistema completo de extremo a extremo:
     - Capacidad del event-loop de Uvicorn y workers de FastAPI.
     - Overhead criptográfico de autenticación (**PBKDF2-HMAC-SHA256 con 100,000 iteraciones**).
     - Serialización/deserialización y validación de esquemas con Pydantic.
     - Límite del pool de conexiones de SQLAlchemy (`DB_POOL_SIZE = 10`, `DB_MAX_OVERFLOW = 20`).
     - Tiempo de inferencia del **RiskEngine** (extracción de 8 features + Random Forest).
     - Serialización forzada por la cadena de auditoría criptográfica (`pg_advisory_xact_lock`).

2. **Prueba Complementaria (Diagnóstico de Persistencia): Base de Datos Aislada**
   - **Por qué:** Si la API colapsa a los $N$ usuarios concurrentes, una prueba directa a PostgreSQL mediante el *JDBC Request Sampler* de JMeter permite aislar si el cuello de botella está en los índices/queries de PostgreSQL o en la capa de aplicación Python.

---

## 2. Tipos de Prueba Soportados

| Tipo de Prueba | Objetivo | Configuración en el Plan |
| :--- | :--- | :--- |
| **Línea Base (Baseline)** | Throughput puro y latencia mínima sin carga de negocio. | 5 hilos, endpoints `/health` y `/ready`. |
| **Carga Normal (Load Test)** | Validar comportamiento bajo volumen esperado de operación. | 25 hilos concurrentes, 10s ramp-up, duración 60s. |
| **Estrés Escalonado (Stress Test)** | Identificar el **Punto de Saturación** y punto de quiebre. | Escalonamiento progresivo: 25 $\rightarrow$ 50 $\rightarrow$ 75 $\rightarrow$ 100 $\rightarrow$ 150 hilos. |
| **Potencia / Pico Súbito (Spike Test)** | Evaluar la resiliencia ante ráfagas repentinas de tráfico. | 100 hilos disparados en 3 segundos sostenidos por 40s. |

---

## 3. Preparación del Entorno

### A. Verificar que el Contenedor de PostgreSQL esté activo
```bash
docker start radar-credenciales-postgres
```
*Mapeo de puertos activo:* `5432` en el contenedor $\rightarrow$ `5433` en el Host.

### B. Iniciar el Backend de FastAPI
Desde la carpeta `backend/` con el entorno virtual activo:
```bash
cd backend
.\.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload
```
Verifica en tu navegador: [http://localhost:8000/health](http://localhost:8000/health).

---

## 4. Ejecución de las Pruebas

### Opción 1: Ejecución Automática por CLI (Recomendada para Medición Científica)
Ejecutar sin entorno gráfico evita que Java Swing consuma memoria y falsee los tiempos de respuesta.

Abre PowerShell en la raíz del proyecto y ejecuta el script automatizado:

```powershell
# 1. Prueba de Línea Base
.\performance\run_tests.ps1 -Type baseline

# 2. Prueba de Carga Normal (25 usuarios concurrentes)
.\performance\run_tests.ps1 -Type load

# 3. Batería de Prueba de Estrés (Iteraciones: 25 -> 50 -> 75 -> 100 -> 150)
.\performance\run_tests.ps1 -Type stress

# 4. Prueba de Pico Súbito (100 usuarios en 3 segundos)
.\performance\run_tests.ps1 -Type spike

# 5. Prueba Personalizada
.\performance\run_tests.ps1 -Type custom -Threads 40 -RampUp 15 -Duration 90
```

> [!TIP]
> Cada ejecución genera automáticamente un **Dashboard HTML interactivo** dentro de `performance/reports/<nombre_prueba>/index.html` con tablas APDEX, percentiles $P_{90}, P_{95}, P_{99}$, gráficos de Throughput vs Latencia y mapa de errores.

---

### Opción 2: Ejecución desde la Interfaz Gráfica (GUI) de JMeter

1. Abre JMeter ejecutando:
   ```cmd
   C:\apache-jmeter-5.6.3\bin\jmeter.bat
   ```
2. Ve a **File $\rightarrow$ Open** y selecciona:
   `c:\Trabajos UNT\CICLO VIII\INGENIERIA DE SOFTWARE II\SEMANA 15\Sistema_RadarCredencialesComprometidas\performance\radar_performance_test.jmx`
3. Verás la estructura en el árbol de la izquierda:
   - `00_Setup_Autenticacion` (*setUp Thread Group* que hace login y obtiene el JWT).
   - `01_Carga_SOC_Plataforma` (*Thread Group* con Dashboard, KPIs y Leaks).
   - `02_Inferencia_ML_Containment` (*Thread Group* opcional para pruebas de contención).
   - `03_Linea_Base_Salud` (*Thread Group* de `/health`).
   - Listeners: `Summary Report`, `Aggregate Report` y `View Results Tree`.
4. Haz clic en el botón verde **Start** (o presiona `Ctrl + R`) para iniciar.

---

## 5. Metodología para Identificar el Punto de Saturación

Para tu informe o artículo académico, registra los resultados de cada escalón del **Stress Test** en una tabla comparativa:

| Hilos (Usuarios) | Throughput (req/s) | Latencia Media (ms) | $P_{95}$ (ms) | % Errores | Estado |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 10 | *Medir* | *Medir* | *Medir* | 0.0% | Zona Estable |
| 25 | *Medir* | *Medir* | *Medir* | 0.0% | Zona Estable |
| 50 | *Medir* | *Medir* | *Medir* | < 1% | Límite Nominal |
| 75 | *Medir* | *Medir* | *Medir* | > 1% | **Punto de Saturación** |
| 100 | *Medir* | *Medir* | *Medir* | > 5% | Zona de Quiebre |

### Criterio de Detección del "Codo de Saturación":
1. **Zona Lineal:** Mientras el Throughput aumente proporcionalmente al número de hilos y la latencia crezca suavemente, el sistema está en capacidad óptima.
2. **Punto de Saturación:** Es el punto exacto donde el Throughput deja de crecer (alcanza una asíntota horizontal) y el percentil 95 ($P_{95}$) se dispara de forma exponencial.
3. **Punto de Quiebre:** Cuando aparecen códigos HTTP 500 o 504 por saturación del pool de SQLAlchemy (`QueuePool limit reached`) o timeouts de red.

---

## 6. Monitoreo Simultáneo durante las Pruebas

Durante la ejecución de JMeter, abre otra terminal y monitorea los recursos en tiempo real:

1. **Uso de CPU y Memoria de PostgreSQL en Docker:**
   ```bash
   docker stats radar-credenciales-postgres
   ```
2. **Métricas en Vivo del Backend (Prometheus):**
   Abre en tu navegador o consulta vía cURL:
   [http://localhost:8000/metrics](http://localhost:8000/metrics)
   Observa los contadores `radar_requests_total` y los histogramas `radar_request_latency_seconds`.


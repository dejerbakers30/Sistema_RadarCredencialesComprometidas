# ==============================================================================
# Script de Automatización de Pruebas de Rendimiento con Apache JMeter 5.6.3
# Sistema: Radar de Credenciales Comprometidas
# ==============================================================================
param (
    [ValidateSet("baseline", "load", "stress", "spike", "custom")]
    [string]$Type = "load",

    [int]$Threads = 25,
    [int]$RampUp = 10,
    [int]$Duration = 60,
    [string]$HostTarget = "localhost",
    [int]$PortTarget = 8000,
    [string]$JMeterBin = "C:\apache-jmeter-5.6.3\bin\jmeter.bat"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$PlanPath = Join-Path $ScriptDir "radar_performance_test.jmx"
$ReportsBaseDir = Join-Path $ScriptDir "reports"
$ResultsBaseDir = Join-Path $ScriptDir "results"

if (-not (Test-Path $JMeterBin)) {
    Write-Error "No se encontró el ejecutable de JMeter en: $JMeterBin. Verifica la ruta."
    exit 1
}

if (-not (Test-Path $PlanPath)) {
    Write-Error "No se encontró el archivo de plan de pruebas en: $PlanPath"
    exit 1
}

# Crear carpetas de salida
if (-not (Test-Path $ReportsBaseDir)) { New-Item -ItemType Directory -Path $ReportsBaseDir -Force | Out-Null }
if (-not (Test-Path $ResultsBaseDir)) { New-Item -ItemType Directory -Path $ResultsBaseDir -Force | Out-Null }

function Execute-JMeterRun {
    param (
        [string]$ScenarioName,
        [int]$NumThreads,
        [int]$RampSeconds,
        [int]$DurationSeconds,
        [string]$ExtraProps = ""
    )

    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $RunId = "${ScenarioName}_th${NumThreads}_${Timestamp}"
    $JtlFile = Join-Path $ResultsBaseDir "${RunId}.jtl"
    $ReportDir = Join-Path $ReportsBaseDir $RunId

    Write-Host "`n======================================================================" -ForegroundColor Cyan
    Write-Host " [RUN] Ejecutando Escenario: $ScenarioName" -ForegroundColor Yellow
    Write-Host "   - Hilos concurrentes (Threads): $NumThreads"
    Write-Host "   - Rampa de subida (Ramp-up):    ${RampSeconds}s"
    Write-Host "   - Duracion de la prueba:        ${DurationSeconds}s"
    Write-Host "   - Destino HTTP:                 http://${HostTarget}:${PortTarget}"
    Write-Host "   - Guardando reporte HTML en:    $ReportDir"
    Write-Host "======================================================================" -ForegroundColor Cyan

    $cmdArgs = @(
        "-n",
        "-t", "`"$PlanPath`"",
        "-l", "`"$JtlFile`"",
        "-e",
        "-o", "`"$ReportDir`"",
        "-Jhost=$HostTarget",
        "-Jport=$PortTarget",
        "-Jthreads=$NumThreads",
        "-Jrampup=$RampSeconds",
        "-Jduration=$DurationSeconds"
    )

    if ($ExtraProps) {
        $cmdArgs += $ExtraProps.Split(" ")
    }

    $cmdString = "& `"$JMeterBin`" " + ($cmdArgs -join " ")
    Invoke-Expression $cmdString

    if (Test-Path $JtlFile) {
        Write-Host "`n[+] Prueba completada exitosamente." -ForegroundColor Green
        Write-Host "    Para ver el Dashboard web interactivo abre:" -ForegroundColor Green
        Write-Host "    file://$($ReportDir -replace '\\', '/')/index.html`n" -ForegroundColor White
    } else {
        Write-Host "`n[!] Advertencia: No se genero el archivo JTL." -ForegroundColor Red
    }
}

# ------------------------------------------------------------------------------
# Selección de tipo de prueba
# ------------------------------------------------------------------------------
switch ($Type) {
    "baseline" {
        Write-Host "`n[*] Iniciando Prueba de Linea Base (Baseline / Smoke)..." -ForegroundColor Magenta
        Execute-JMeterRun -ScenarioName "Baseline" -NumThreads 5 -RampSeconds 2 -DurationSeconds 30 -ExtraProps "-Jenable_baseline=true"
    }

    "load" {
        Write-Host "`n[*] Iniciando Prueba de Carga Normal (Load Test - 25 usuarios)..." -ForegroundColor Magenta
        Execute-JMeterRun -ScenarioName "LoadTest" -NumThreads 25 -RampSeconds 10 -DurationSeconds 60
    }

    "stress" {
        Write-Host "`n[*] Iniciando Bateria de Prueba de Estres Escalonada (Stress Test)..." -ForegroundColor Magenta
        Write-Host "Se ejecutaran iteraciones sucesivas para hallar el Punto de Saturacion:`n" -ForegroundColor DarkYellow
        
        $stepArray = @(25, 50, 75, 100, 150)
        foreach ($th in $stepArray) {
            Write-Host ">>> Paso de Estres con $th hilos simultaneos..." -ForegroundColor Cyan
            Execute-JMeterRun -ScenarioName "Stress_Step" -NumThreads $th -RampSeconds ([math]::Max(5, [int]($th/5))) -DurationSeconds 60
            Write-Host "Pausa de enfriamiento (cooldown) de 10 segundos..." -ForegroundColor Gray
            Start-Sleep -Seconds 10
        }
    }

    "spike" {
        Write-Host "`n[*] Iniciando Prueba de Potencia / Pico Súbito (Spike Test)..." -ForegroundColor Magenta
        Write-Host "Salto brusco de 100 usuarios en 3 segundos sostenidos por 40 segundos..." -ForegroundColor DarkYellow
        Execute-JMeterRun -ScenarioName "SpikeTest" -NumThreads 100 -RampSeconds 3 -DurationSeconds 40
    }

    "custom" {
        Write-Host "`n[*] Iniciando Prueba Personalizada..." -ForegroundColor Magenta
        Execute-JMeterRun -ScenarioName "CustomTest" -NumThreads $Threads -RampSeconds $RampUp -DurationSeconds $Duration
    }
}


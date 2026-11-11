"""Script de Entrenamiento y Validación Científica del Motor de Riesgo (RockYou Dataset).

Cumple con los requisitos académicos de validación:
1. Lectura del dataset real RockYou (10,000 contraseñas reales).
2. Generación de etiquetas heurísticas Ground Truth (NIST / Top 100 RockYou):
   - Débil: Longitud < 8 caracteres o presente en el Top 100 de RockYou.
   - No Débil: Longitud >= 8 caracteres y fuera del Top 100.
3. División estratificada: 70% Entrenamiento (Train), 15% Validación (Val), 15% Prueba (Test).
4. Entrenamiento de clasificador de Machine Learning (RandomForestClassifier).
5. Evaluación comparativa en Train, Val y Test: Accuracy, Precisión, Recall y F1-Score.
6. Matriz de Confusión específica para el conjunto de Prueba (Test).
7. Exportación de métricas a 'backend/data/metrics_results.json' para artículo científico.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Añadir backend a sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from app.services.risk_engine import extract_features


def load_and_label_dataset(
    file_path: Path, limit: int = 10000
) -> tuple[list[str], np.ndarray, np.ndarray, set[str]]:
    """Lee contraseñas reales y genera matriz de características X y etiquetas y."""
    if not file_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de dataset en: {file_path}")

    passwords: list[str] = []
    top_100_passwords: set[str] = set()

    with open(file_path, "r", encoding="latin-1", errors="replace") as f:
        for line in f:
            pwd = line.rstrip("\r\n")
            if not pwd:
                continue
            if len(top_100_passwords) < 100:
                top_100_passwords.add(pwd.lower())

            passwords.append(pwd)
            if len(passwords) >= limit:
                break

    X_list: list[list[float]] = []
    y_list: list[str] = []

    for pwd in passwords:
        # Extracción de características
        features = extract_features(pwd)
        X_list.append(features)

        # Regla Heurística Ground Truth (NIST SP 800-63B / Top 100 RockYou)
        is_weak = (len(pwd) < 8) or (pwd.lower() in top_100_passwords)
        y_list.append("Débil" if is_weak else "No Débil")

    return passwords, np.array(X_list), np.array(y_list), top_100_passwords


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Calcula métricas clave para la clase de interés 'Débil'."""
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, pos_label="Débil", zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, pos_label="Débil", zero_division=0)),
        "f1_score": float(f1_score(y_true, y_pred, pos_label="Débil", zero_division=0)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validación científica del Risk Engine (70/15/15)")
    parser.add_argument(
        "--file",
        type=str,
        default=str(BASE_DIR / "data" / "rockyou_sample.txt"),
        help="Ruta al dataset RockYou real",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10000,
        help="Número de muestras reales a procesar (default: 10000)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(BASE_DIR / "data" / "metrics_results.json"),
        help="Archivo JSON de salida para métricas",
    )
    args = parser.parse_args()

    data_path = Path(args.file)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("================================================================================")
    print("   VALIDACIÓN CIENTÍFICA: MOTOR DE RIESGO DE MACHINE LEARNING (ROCKYOU DATASET) ")
    print("================================================================================")
    print(f"Dataset de entrada : {data_path}")
    print(f"Muestras a evaluar : {args.limit:,}")
    print("--------------------------------------------------------------------------------\n")

    # 1. Carga y etiquetado
    passwords, X, y, top100 = load_and_label_dataset(data_path, limit=args.limit)
    total_muestras = len(passwords)
    conteo_clases = pd.Series(y).value_counts()
    print("Distribución Global del Ground Truth:")
    for cls_name, count in conteo_clases.items():
        print(f"  - {cls_name}: {count:,} ({count / total_muestras * 100:.2f}%)")
    print("\n--------------------------------------------------------------------------------")

    # 2. División Estratificada (70% Train, 15% Val, 15% Test)
    # Paso 1: Separar 70% Train y 30% Temporal
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )

    # Paso 2: Dividir el 30% en dos partes iguales de 15% (Val y Test)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
    )

    print(f"División de Datos (Estratificada):")
    print(f"  - Entrenamiento (Train 70%) : {len(y_train):,} muestras")
    print(f"  - Validación    (Val   15%) : {len(y_val):,} muestras")
    print(f"  - Prueba        (Test  15%) : {len(y_test):,} muestras")
    print("--------------------------------------------------------------------------------\n")

    # 3. Entrenamiento del Modelo (RandomForestClassifier)
    print("[*] Entrenando modelo RandomForestClassifier sobre conjunto de Train...")
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)
    print("[+] Entrenamiento completado exitosamente.\n")

    # 4. Inferencia en los tres conjuntos
    y_pred_train = clf.predict(X_train)
    y_pred_val = clf.predict(X_val)
    y_pred_test = clf.predict(X_test)

    metrics_train = compute_metrics(y_train, y_pred_train)
    metrics_val = compute_metrics(y_val, y_pred_val)
    metrics_test = compute_metrics(y_test, y_pred_test)

    # 5. Tabla Comparativa de Rendimiento (Train vs Val vs Test)
    table_data = {
        "Métrica": [
            "Muestras Evaluadas",
            "Exactitud (Accuracy)",
            "Precisión (Clase Débil)",
            "Sensibilidad / Recall (Clase Débil)",
            "Puntuación F1 (F1-Score)",
        ],
        "Entrenamiento (Train 70%)": [
            f"{len(y_train):,}",
            f"{metrics_train['accuracy'] * 100:.2f}%",
            f"{metrics_train['precision'] * 100:.2f}%",
            f"{metrics_train['recall'] * 100:.2f}%",
            f"{metrics_train['f1_score'] * 100:.2f}%",
        ],
        "Validación (Val 15%)": [
            f"{len(y_val):,}",
            f"{metrics_val['accuracy'] * 100:.2f}%",
            f"{metrics_val['precision'] * 100:.2f}%",
            f"{metrics_val['recall'] * 100:.2f}%",
            f"{metrics_val['f1_score'] * 100:.2f}%",
        ],
        "Prueba (Test 15%)": [
            f"{len(y_test):,}",
            f"{metrics_test['accuracy'] * 100:.2f}%",
            f"{metrics_test['precision'] * 100:.2f}%",
            f"{metrics_test['recall'] * 100:.2f}%",
            f"{metrics_test['f1_score'] * 100:.2f}%",
        ],
    }

    comparison_df = pd.DataFrame(table_data)

    print("================================================================================")
    print(" 1. TABLA COMPARATIVA DE RENDIMIENTO (TRAIN vs VALIDATION vs TEST)")
    print("================================================================================")
    print(comparison_df.to_string(index=False))
    print("================================================================================\n")

    # 6. Matriz de Confusión Exclusiva para el Conjunto de Prueba (Test)
    labels = ["Débil", "No Débil"]
    cm_test = confusion_matrix(y_test, y_pred_test, labels=labels)
    cm_test_df = pd.DataFrame(
        cm_test,
        index=[f"Real: {l}" for l in labels],
        columns=[f"Pred: {l}" for l in labels],
    )

    tn, fp, fn, tp = (
        cm_test[1, 1],
        cm_test[1, 0],
        cm_test[0, 1],
        cm_test[0, 0],
    )

    print("================================================================================")
    print(" 2. MATRIZ DE CONFUSIÓN — CONJUNTO DE PRUEBA (TEST 15%)")
    print("================================================================================")
    print(cm_test_df.to_string())
    print("--------------------------------------------------------------------------------")
    print(f"  - Verdaderos Positivos (TP - Débil detectado)     : {tp:,}")
    print(f"  - Falsos Negativos    (FN - Débil no detectado)   : {fn:,}")
    print(f"  - Verdaderos Negativos (TN - No Débil detectado)  : {tn:,}")
    print(f"  - Falsos Positivos    (FP - No Débil marcado err.): {fp:,}")
    print("================================================================================\n")

    # Reporte detallado de clasificación sobre Test
    test_report_dict = classification_report(
        y_test, y_pred_test, labels=labels, output_dict=True, zero_division=0
    )

    # 7. Guardar resultados en archivo JSON para artículo científico
    export_payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset": {
            "archivo": data_path.name,
            "total_muestras": total_muestras,
            "distribucion_ground_truth": {
                k: int(v) for k, v in conteo_clases.items()
            },
        },
        "division_estratificada": {
            "ratios": {"train": 0.70, "validation": 0.15, "test": 0.15},
            "muestras": {
                "train": len(y_train),
                "validation": len(y_val),
                "test": len(y_test),
            },
        },
        "modelo": {
            "algoritmo": "RandomForestClassifier",
            "hiperparametros": {
                "n_estimators": 100,
                "max_depth": 12,
                "class_weight": "balanced",
                "random_state": 42,
            },
        },
        "metricas_comparativas": {
            "train": metrics_train,
            "validation": metrics_val,
            "test": metrics_test,
        },
        "matriz_confusion_test": {
            "labels": labels,
            "matriz": cm_test.tolist(),
            "verdaderos_positivos": int(tp),
            "falsos_positivos": int(fp),
            "verdaderos_negativos": int(tn),
            "falsos_negativos": int(fn),
        },
        "reporte_clasificacion_test": test_report_dict,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_payload, f, indent=2, ensure_ascii=False)

    print(f"[+] Resultados guardados exitosamente en: {output_path}")
    print("================================================================================\n")


if __name__ == "__main__":
    main()

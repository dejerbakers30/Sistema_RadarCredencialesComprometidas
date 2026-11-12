"""Análisis complementario del clasificador de riesgo (RockYou, partición 70/15/15, semilla 42).

Complementa ``evaluate_model.py`` sin modificarlo. Reutiliza su carga, su etiquetado y su
partición, y calcula con los mismos datos:

1. Procedencia de la muestra (huella SHA-256, duplicados exactos y en minúsculas).
2. Matrices de confusión exactas de entrenamiento, validación y prueba.
3. Solapamiento de contraseñas entre entrenamiento y prueba.
4. Caracterización de los falsos negativos de prueba (longitud y pertenencia al top-100).
5. Líneas base: clase mayoritaria, regla L < 8, regresión logística y árbol de decisión.
6. Validación cruzada estratificada repetida (5 pliegues x 5 repeticiones).
7. Comportamiento del motor de producción de tres niveles sobre la partición de prueba.
8. Intervalos de confianza (Wilson, bootstrap multinomial, regla de tres) y pruebas exactas.

No imprime contraseñas individuales. Uso:

    python analisis_extra.py --file data/rockyou_sample.txt --output data/analisis_extra_results.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
from scipy.stats import fisher_exact
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, matthews_corrcoef
from sklearn.model_selection import RepeatedStratifiedKFold, train_test_split
from sklearn.tree import DecisionTreeClassifier

from app.services.risk_engine import risk_engine
from evaluate_model import load_and_label_dataset

SEED = 42
POS = "Débil"
NEG = "No Débil"
Z = 1.959964


def wilson(k: int, n: int, z: float = Z) -> tuple[float, float]:
    """Intervalo de Wilson para una proporción k/n."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / den
    mitad = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, centro - mitad), min(1.0, centro + mitad))


def cm_counts(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, int]:
    """Recuentos VP/FP/FN/VN con la clase Débil como positiva."""
    m = confusion_matrix(y_true, y_pred, labels=[POS, NEG])
    return {"VP": int(m[0, 0]), "FN": int(m[0, 1]), "FP": int(m[1, 0]), "VN": int(m[1, 1])}


def metrics_from(c: dict[str, int]) -> dict[str, float]:
    vp, fp, fn, vn = c["VP"], c["FP"], c["FN"], c["VN"]
    n = vp + fp + fn + vn
    prec = vp / (vp + fp) if vp + fp else float("nan")
    rec = vp / (vp + fn) if vp + fn else float("nan")
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else float("nan")
    den = math.sqrt((vp + fp) * (vp + fn) * (vn + fp) * (vn + fn))
    mcc = (vp * vn - fp * fn) / den if den else float("nan")
    return {
        "n": n,
        "accuracy": (vp + vn) / n,
        "precision": prec,
        "recall": rec,
        "specificity": vn / (vn + fp) if vn + fp else float("nan"),
        "npv": vn / (vn + fn) if vn + fn else float("nan"),
        "f1": f1,
        "mcc": mcc,
        "fnr": fn / (vp + fn) if vp + fn else float("nan"),
        "fpr": fp / (vn + fp) if vn + fp else float("nan"),
    }


def bootstrap_ci(c: dict[str, int], reps: int = 10_000) -> dict[str, list[float]]:
    """Bootstrap paramétrico multinomial sobre los recuentos de la matriz."""
    rng = np.random.default_rng(SEED)
    n = sum(c.values())
    probs = np.array([c["VP"], c["FP"], c["FN"], c["VN"]], dtype=float) / n
    draws = rng.multinomial(n, probs, size=reps)
    vp, fp, fn, vn = (draws[:, i].astype(float) for i in range(4))
    with np.errstate(divide="ignore", invalid="ignore"):
        f1 = 2 * vp / (2 * vp + fp + fn)
        den = np.sqrt((vp + fp) * (vp + fn) * (vn + fp) * (vn + fn))
        mcc = (vp * vn - fp * fn) / den
    out = {}
    for name, arr in (("f1", f1), ("mcc", mcc)):
        arr = arr[np.isfinite(arr)]
        out[name] = [float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))]
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Análisis complementario del clasificador RockYou")
    ap.add_argument("--file", default=str(BASE_DIR / "data" / "rockyou_sample.txt"))
    ap.add_argument("--limit", type=int, default=10000)
    ap.add_argument("--output", default=str(BASE_DIR / "data" / "analisis_extra_results.json"))
    args = ap.parse_args()
    path = Path(args.file)

    passwords, X, y, top100 = load_and_label_dataset(path, limit=args.limit)
    lengths = np.array([len(p) for p in passwords])
    lowers = [p.lower() for p in passwords]
    res: dict = {}

    # 1. Procedencia de la muestra
    res["muestra"] = {
        "archivo": path.name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "lineas": len(passwords),
        "distintas_exactas": len(set(passwords)),
        "distintas_en_minusculas": len(set(lowers)),
        "duplicados_en_minusculas": len(passwords) - len(set(lowers)),
        "longitud_mediana": float(np.median(lengths)),
        "longitud_minima": int(lengths.min()),
        "longitud_maxima": int(lengths.max()),
        "proporcion_L_menor_8": float((lengths < 8).mean()),
        "positivos_con_L_mayor_igual_8": int(((y == POS) & (lengths >= 8)).sum()),
        "top100_distintas": len(top100),
    }

    # 2. Partición idéntica a evaluate_model.py (se parte el índice, no las matrices)
    idx = np.arange(len(y))
    i_tr, i_tmp, y_tr, y_tmp = train_test_split(idx, y, test_size=0.30, random_state=SEED, stratify=y)
    i_va, i_te, y_va, y_te = train_test_split(i_tmp, y_tmp, test_size=0.50, random_state=SEED, stratify=y_tmp)

    clf = RandomForestClassifier(n_estimators=100, max_depth=12, class_weight="balanced", random_state=SEED, n_jobs=-1)
    clf.fit(X[i_tr], y_tr)
    preds = {"train": clf.predict(X[i_tr]), "validation": clf.predict(X[i_va]), "test": clf.predict(X[i_te])}
    ys = {"train": y_tr, "validation": y_va, "test": y_te}

    res["matrices_exactas"] = {}
    for k in preds:
        c = cm_counts(ys[k], preds[k])
        c["positivos"] = c["VP"] + c["FN"]
        c["negativos"] = c["VN"] + c["FP"]
        res["matrices_exactas"][k] = {**c, **metrics_from(c)}

    # 3. Solapamiento entrenamiento-prueba
    tr_exact = {passwords[i] for i in i_tr}
    tr_lower = {lowers[i] for i in i_tr}
    te_pw = [passwords[i] for i in i_te]
    te_lo = [lowers[i] for i in i_te]
    res["solapamiento_train_test"] = {
        "prueba_n": len(te_pw),
        "exactas_en_train": int(sum(p in tr_exact for p in te_pw)),
        "minusculas_en_train": int(sum(p in tr_lower for p in te_lo)),
    }

    # 4. Falsos negativos de prueba (sin publicar contraseñas)
    fn_mask = (y_te == POS) & (preds["test"] == NEG)
    fn_idx = i_te[fn_mask]
    fn_len = lengths[fn_idx]
    res["falsos_negativos_test"] = {
        "n": int(fn_mask.sum()),
        "longitud_min": int(fn_len.min()) if len(fn_len) else None,
        "longitud_max": int(fn_len.max()) if len(fn_len) else None,
        "con_L_menor_8": int((fn_len < 8).sum()),
        "con_L_mayor_igual_8": int((fn_len >= 8).sum()),
        "en_top100": int(sum(lowers[i] in top100 for i in fn_idx)),
        "con_patron_comun": int(sum(X[i][5] == 1.0 for i in fn_idx)),
    }
    te_pos_long = (y_te == POS) & (lengths[i_te] >= 8)
    res["positivos_test_con_L_mayor_igual_8"] = {
        "n": int(te_pos_long.sum()),
        "recuperados_por_rf": int((preds["test"][te_pos_long] == POS).sum()),
        "recuperados_por_regla_L8": 0,
    }

    # 5. Líneas base en prueba
    y_te_bin = (y_te == POS).astype(int)
    base: dict[str, dict] = {}
    pred_maj = np.full(len(y_te), POS)
    pred_rule = np.where(lengths[i_te] < 8, POS, NEG)
    for name, p in (("mayoritaria", pred_maj), ("regla_L_menor_8", pred_rule)):
        c = cm_counts(y_te, p)
        base[name] = {**c, **metrics_from(c)}
    lr = LogisticRegression(class_weight="balanced", max_iter=5000, random_state=SEED)
    lr.fit(X[i_tr], y_tr)
    dt = DecisionTreeClassifier(max_depth=12, class_weight="balanced", random_state=SEED)
    dt.fit(X[i_tr], y_tr)
    for name, model in (("regresion_logistica", lr), ("arbol_decision", dt)):
        c = cm_counts(y_te, model.predict(X[i_te]))
        base[name] = {**c, **metrics_from(c)}
    res["lineas_base_test"] = base
    _ = y_te_bin

    # 6. Validación cruzada repetida (5x5) sobre las 10 000 muestras
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=SEED)
    cv_rows = {"rf": [], "regla_L8": []}
    for a, b in cv.split(X, y):
        m = RandomForestClassifier(n_estimators=100, max_depth=12, class_weight="balanced", random_state=SEED, n_jobs=-1)
        m.fit(X[a], y[a])
        for key, pred in (("rf", m.predict(X[b])), ("regla_L8", np.where(lengths[b] < 8, POS, NEG))):
            cc = cm_counts(y[b], pred)
            mm = metrics_from(cc)
            cv_rows[key].append([mm["accuracy"], mm["precision"], mm["recall"], mm["f1"], mm["fnr"]])
    res["validacion_cruzada_5x5"] = {}
    for key, rows in cv_rows.items():
        arr = np.array(rows)
        res["validacion_cruzada_5x5"][key] = {
            nm: {"media": float(arr[:, j].mean()), "desv": float(arr[:, j].std(ddof=1)), "min": float(arr[:, j].min()), "max": float(arr[:, j].max())}
            for j, nm in enumerate(["accuracy", "precision", "recall", "f1", "fnr"])
        }
    res["validacion_cruzada_5x5"]["n_particiones"] = len(cv_rows["rf"])
    rf_arr, rule_arr = np.array(cv_rows["rf"]), np.array(cv_rows["regla_L8"])
    dif = rf_arr - rule_arr  # columnas: accuracy, precision, recall, f1, fnr
    res["validacion_cruzada_5x5"]["comparacion_pareada_rf_menos_regla"] = {
        "dif_media_accuracy": float(dif[:, 0].mean()),
        "dif_media_recall": float(dif[:, 2].mean()),
        "pliegues_rf_mejor_accuracy": int((dif[:, 0] > 1e-12).sum()),
        "pliegues_empate_accuracy": int((np.abs(dif[:, 0]) <= 1e-12).sum()),
        "pliegues_rf_peor_accuracy": int((dif[:, 0] < -1e-12).sum()),
    }

    # 7. Motor de producción (tres niveles) sobre la partición de prueba
    niveles = [risk_engine.evaluate(passwords[i]) for i in i_te]
    tabla: dict[str, dict[str, int]] = {n: {POS: 0, NEG: 0} for n in ("Bajo", "Medio", "Crítico")}
    for nivel, etiqueta in zip(niveles, y_te):
        tabla[nivel][str(etiqueta)] += 1
    res["motor_produccion_test"] = {"tabla_nivel_vs_etiqueta": tabla}
    for nombre, positivos in (("critico_es_positivo", {"Crítico"}), ("medio_o_critico_es_positivo", {"Medio", "Crítico"})):
        pred = np.array([POS if n in positivos else NEG for n in niveles])
        c = cm_counts(y_te, pred)
        res["motor_produccion_test"][nombre] = {**c, **metrics_from(c)}

    # 8. Intervalos y pruebas exactas sobre la prueba
    ct = res["matrices_exactas"]["test"]
    cnt = {k: ct[k] for k in ("VP", "FP", "FN", "VN")}
    n = sum(cnt.values())
    ci = {
        "exactitud": wilson(cnt["VP"] + cnt["VN"], n),
        "precision": wilson(cnt["VP"], cnt["VP"] + cnt["FP"]),
        "recall": wilson(cnt["VP"], cnt["VP"] + cnt["FN"]),
        "especificidad": wilson(cnt["VN"], cnt["VN"] + cnt["FP"]),
        "npv": wilson(cnt["VN"], cnt["VN"] + cnt["FN"]),
        "fnr": wilson(cnt["FN"], cnt["VP"] + cnt["FN"]),
    }
    res["intervalos_test"] = {k: [float(a), float(b)] for k, (a, b) in ci.items()}
    res["intervalos_test"].update(bootstrap_ci(cnt))
    res["intervalos_test"]["regla_de_tres_fpr_superior"] = 3 / ct["negativos"]
    tr, va = res["matrices_exactas"]["train"], res["matrices_exactas"]["validation"]
    res["fisher_fnr"] = {
        "train_vs_test_p": float(fisher_exact([[ct["FN"], ct["VP"]], [tr["FN"], tr["VP"]]])[1]),
        "validation_vs_test_p": float(fisher_exact([[ct["FN"], ct["VP"]], [va["FN"], va["VP"]]])[1]),
        "train_fnr": tr["fnr"], "validation_fnr": va["fnr"], "test_fnr": ct["fnr"],
    }
    for k, key in (("train", "train"), ("validation", "validation")):
        m = res["matrices_exactas"][key]
        res["matrices_exactas"][key]["fnr_wilson"] = list(wilson(m["FN"], m["positivos"]))
    s, tfp = ct["recall"], res["intervalos_test"]["regla_de_tres_fpr_superior"]
    res["escenarios_prevalencia"] = {
        f"{int(p * 100)}%": s * p / (s * p + tfp * (1 - p)) for p in (0.10, 0.01)
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

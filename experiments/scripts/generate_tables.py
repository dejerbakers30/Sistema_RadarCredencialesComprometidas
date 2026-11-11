"""Generate the six experiment tables only from result files."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from common import PROCESSED, RESULTS, TABLES, ensure_dirs, read_json, write_csv  # noqa: E402


def rows(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def md(path: Path, title: str, data: list[dict]) -> None:
    if not data:
        path.write_text(f"# {title}\n\nNO MEDIDA\n", encoding="utf-8"); return
    keys = list(data[0])
    lines = [f"# {title}", "", "| " + " | ".join(keys) + " |", "| " + " | ".join(["---"] * len(keys)) + " |"]
    lines.extend("| " + " | ".join(str(r.get(k, "")) for k in keys) + " |" for r in data)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ensure_dirs()
    detection = rows(RESULTS / "detection_cases.csv")
    metrics = read_json(RESULTS / "detection_metrics.json")
    idempotency = rows(RESULTS / "idempotency.csv")
    containment = rows(RESULTS / "containment_trials.csv")
    backend = read_json(RESULTS / "backend_pipeline_summary.json")
    n8n = read_json(RESULTS / "n8n_e2e_summary.json")
    duplicates = read_json(RESULTS / "n8n_duplicate_control.json")
    integrity = read_json(RESULTS / "audit_integrity.json")
    dataset = rows(PROCESSED / "hibp_test_accounts.csv")
    table1 = [{"cases": len(dataset), "positive_labels": sum(r["expected_positive"] == "True" for r in dataset), "negative_labels": sum(r["expected_positive"] == "False" for r in dataset), "source": "HIBP official integration tests"}]
    table3 = [{k: v for k, v in metrics.items() if k in {"TP", "TN", "FP", "FN", "accuracy", "precision", "recall", "specificity", "f1"}}]
    table5 = [{"scenario": s, "n": len([r for r in containment if r["scenario"] == s]), "successes": sum(r["result"] == "exitoso" for r in containment if r["scenario"] == s), "mean_attempts": sum(float(r["attempts"]) for r in containment if r["scenario"] == s) / len([r for r in containment if r["scenario"] == s])} for s in sorted({r["scenario"] for r in containment})]
    table6 = [{"backend_pipeline_n": backend.get("n_runs_completed", backend.get("n_total")), "backend_mean_ms": backend.get("mean_ms"), "n8n_e2e_n": n8n.get("n_total"), "n8n_e2e_successes": n8n.get("n_success"), "n8n_e2e_mean_ms": n8n.get("mean_ms"), "duplicate_replays": duplicates.get("replays"), "new_duplicate_hits": duplicates.get("new_leak_hits"), "audit_before": integrity["before_tamper_ok"], "audit_after_tamper": integrity["after_tamper_ok"], "audit_restored": integrity["restored_ok"]}]
    outputs = [("table1_dataset.csv", table1, "Tabla 1 — Dataset"), ("table2_detection.csv", detection, "Tabla 2 — Detección"), ("table3_metrics.csv", table3, "Tabla 3 — Métricas"), ("table4_idempotency.csv", idempotency, "Tabla 4 — Idempotencia"), ("table5_containment.csv", table5, "Tabla 5 — Contención"), ("table6_summary.csv", table6, "Tabla 6 — Resumen")]
    for filename, data, title in outputs:
        write_csv(TABLES / filename, data[0].keys() if data else ["status"], data or [{"status": "NO MEDIDA"}])
        md(TABLES / filename.replace(".csv", ".md"), title, data)
    print(f"tables_generated={len(outputs)}")
    return 0


if __name__ == "__main__": raise SystemExit(main())

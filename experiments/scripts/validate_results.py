"""Validate that result artifacts exist and are internally reproducible."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from common import FIGURES, PROCESSED, PROVENANCE, RAW, RESULTS, TABLES, read_json, sha256_file  # noqa: E402


def main() -> int:
    required = [PROCESSED / "hibp_test_accounts.csv", RESULTS / "detection_cases.csv", RESULTS / "detection_metrics.json", RESULTS / "idempotency.csv", RESULTS / "containment_trials.csv", RESULTS / "backend_pipeline_latency.csv", RESULTS / "backend_pipeline_summary.json", RESULTS / "n8n_preflights.csv", RESULTS / "n8n_e2e_latency.csv", RESULTS / "n8n_e2e_summary.json", RESULTS / "n8n_duplicate_control.json", RESULTS / "audit_integrity.json"]
    missing = [str(p) for p in required if not p.exists() or p.stat().st_size == 0]
    figures = sorted(FIGURES.glob("*.png")); tables = sorted(TABLES.glob("*.csv"))
    checks = {"required_files": len(required) - len(missing), "missing": missing, "figures": len(figures), "tables": len(tables), "nonempty_figures": all(p.stat().st_size > 0 for p in figures)}
    if not missing and len(figures) == 6 and len(tables) == 6 and checks["nonempty_figures"]:
        metrics = json.loads((RESULTS / "detection_metrics.json").read_text())
        with (RESULTS / "detection_cases.csv").open(encoding="utf-8") as h: rows = list(csv.DictReader(h))
        tp = sum(r["expected_positive"] == "True" and r["radar_match"] == "True" for r in rows); tn = sum(r["expected_positive"] == "False" and r["radar_match"] == "False" for r in rows)
        checks["metrics_match"] = tp == metrics["TP"] and tn == metrics["TN"] and len(rows) == metrics["n"]
    else: checks["metrics_match"] = False
    checks["ok"] = not missing and checks["figures"] == 6 and checks["tables"] == 6 and checks["nonempty_figures"] and checks["metrics_match"]
    provenance = read_json(PROVENANCE / "sources.json") if (PROVENANCE / "sources.json").exists() else {}
    run_dir = RAW / provenance.get("experiment_run", "").replace(":", "").replace("+", "_")
    checks["provenance_hashes_match"] = all(
        (run_dir / source["raw_file"]).exists() and sha256_file(run_dir / source["raw_file"]) == source["sha256"]
        for source in provenance.get("sources", [])
    ) and bool(provenance.get("sources"))
    n8n_rows = list(csv.DictReader((RESULTS / "n8n_e2e_latency.csv").open(encoding="utf-8"))) if (RESULTS / "n8n_e2e_latency.csv").exists() else []
    preflight_rows = list(csv.DictReader((RESULTS / "n8n_preflights.csv").open(encoding="utf-8"))) if (RESULTS / "n8n_preflights.csv").exists() else []
    n8n_summary = read_json(RESULTS / "n8n_e2e_summary.json") if (RESULTS / "n8n_e2e_summary.json").exists() else {}
    duplicate_control = read_json(RESULTS / "n8n_duplicate_control.json") if (RESULTS / "n8n_duplicate_control.json").exists() else {}
    checks["n8n_trials"] = len(n8n_rows) == 30 and all(r.get("result") == "success" for r in n8n_rows)
    checks["n8n_execution_ids"] = all(all(r.get(k) for k in ("w01_execution_id", "w02_execution_id", "w03_execution_id", "w14_execution_id", "w15_execution_id", "w13_execution_ids")) for r in n8n_rows)
    checks["n8n_notification_latency"] = all(r.get("notification_ms") not in ("", "NA", "0", "0.0", None) for r in n8n_rows)
    checks["n8n_summary"] = n8n_summary.get("n_total") == 30 and n8n_summary.get("n_success") == 30 and n8n_summary.get("n_fail") == 0
    checks["preflights"] = len(preflight_rows) == 3 and all(r.get("result") == "success" for r in preflight_rows)
    checks["duplicate_control"] = duplicate_control.get("replays") == 5 and duplicate_control.get("new_leak_hits") == 0 and duplicate_control.get("duplicate_suppression_rate") == 1.0
    checks["ok"] = checks["ok"] and checks["provenance_hashes_match"] and all(checks[k] for k in ("n8n_trials", "n8n_execution_ids", "n8n_notification_latency", "n8n_summary", "preflights", "duplicate_control"))
    print(json.dumps(checks, ensure_ascii=False))
    return 0 if checks["ok"] else 2


if __name__ == "__main__": raise SystemExit(main())

"""Apply the production severity rule to the acquired official catalogue."""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from common import RAW, RESULTS, ensure_dirs, read_json, write_csv, write_json  # noqa: E402


def main() -> int:
    ensure_dirs(); run_dir = sorted(RAW.glob("20*/breaches.json"))[-1].parent
    catalog = read_json(run_dir / "breaches.json")
    import os; os.chdir(Path(__file__).resolve().parents[2] / "backend")
    from app.services.correlation import infer_severity
    rows = []
    for breach in catalog:
        data_classes = breach.get("DataClasses", []) or []
        rows.append({"breach": breach.get("Name", ""), "DataClasses": ";".join(data_classes), "severity": infer_severity(breach).value, "rule": "production app infer_severity(SEVERITY_MAP), maximum mapped severity; empty -> media"})
    write_csv(RESULTS / "severity_distribution.csv", rows[0].keys(), rows)
    counts = Counter(r["severity"] for r in rows); total = len(rows)
    write_json(RESULTS / "severity_summary.json", {k: {"count": counts.get(k, 0), "percentage": round(counts.get(k, 0) / total * 100, 6) if total else "NO MEDIDA"} for k in ("baja", "media", "alta", "critica")})
    print({k: counts.get(k, 0) for k in ("baja", "media", "alta", "critica")})
    return 0


if __name__ == "__main__": raise SystemExit(main())

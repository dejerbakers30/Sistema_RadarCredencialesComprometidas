"""Run the official-account detection cases through the real backend service."""

from __future__ import annotations

import asyncio
import csv
import json
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from common import PROCESSED, RESULTS, RAW, ensure_dirs, read_json, utc_now, write_csv, write_json  # noqa: E402


class SnapshotHIBP:
    def __init__(self, breaches: dict[str, list[str]], catalogue: list[dict]):
        self.breaches = breaches
        self.catalogue = catalogue
        self.base_url = "https://haveibeenpwned.com/api/v3"

    async def breached_domain(self, _domain: str) -> dict[str, list[str]]:
        return self.breaches

    async def all_breaches(self) -> list[dict]:
        return self.catalogue


def latest_raw() -> Path:
    runs = sorted(RAW.glob("20*/breaches.json"))
    if not runs:
        raise FileNotFoundError("No HIBP acquisition found; run 01_fetch_hibp_dataset.py first")
    return runs[-1].parent


async def run() -> int:
    ensure_dirs()
    run_dir = latest_raw()
    catalogue = json.loads((run_dir / "breaches.json").read_text(encoding="utf-8"))
    accounts = list(csv.DictReader((PROCESSED / "hibp_test_accounts.csv").open(encoding="utf-8")))
    account_maps: list[tuple[dict, dict]] = []
    for row in accounts:
        payload = json.loads((run_dir / "accounts" / f"{row['case_id']}.json").read_text(encoding="utf-8") or "[]")
        names = [item["Name"] for item in payload] if isinstance(payload, list) else []
        account_maps.append((row, {row["email"]: names}))

    import os
    os.chdir(Path(__file__).resolve().parents[2] / "backend")
    from sqlalchemy import select
    from app.db.session import SessionLocal
    from app.db.models.leak import LeakHit
    from app.db.models.user import Role, Usuario
    from app.services.correlation import collect_and_correlate

    rows: list[dict] = []
    for source, mapping in account_maps:
        started = time.perf_counter()
        email = source["email"]
        db = SessionLocal()
        error = ""
        try:
            role = db.execute(select(Role).order_by(Role.id)).scalars().first()
            if role is None:
                raise RuntimeError("No role exists in the configured PostgreSQL database")
            user = db.execute(select(Usuario).where(Usuario.email == email)).scalar_one_or_none()
            if user is None:
                user = Usuario(email=email, nombre=f"HIBP experiment {source['case_id']}", rol_id=role.id, activo=True)
                db.add(user)
                db.flush()
            hits = await collect_and_correlate(db, SnapshotHIBP(mapping, catalogue), "hibp-integration-tests.com")
            db.commit()
            hit = db.execute(select(LeakHit).where(LeakHit.email_corporativo == email)).scalars().first()
            radar_match = hit is not None
            hit_id = str(hit.id) if hit else ""
            observed = int(source["observed_breach_count"])
            expected = source["expected_positive"].lower() == "true"
            correct = radar_match == expected
            new_hits = len(hits)
        except Exception as exc:  # retain failure as an experimental observation
            db.rollback()
            radar_match = False
            hit_id = ""
            new_hits = 0
            correct = False
            observed = int(source["observed_breach_count"])
            expected = source["expected_positive"].lower() == "true"
            error = type(exc).__name__ + ": " + str(exc)
        finally:
            db.close()
        rows.append({
            "case_id": source["case_id"], "email": email,
            "expected_positive": expected, "observed_breach_count": observed,
            "radar_match": radar_match, "new_leak_hits": new_hits,
            "leak_hit_id": hit_id, "is_correct": correct,
            "duration_ms": round((time.perf_counter() - started) * 1000, 3),
            "execution_id": "NO MEDIDA (backend service invocation; no n8n execution)",
            "error": error, "retrieved_at": utc_now(),
        })
    write_csv(RESULTS / "detection_cases.csv", rows[0].keys(), rows)
    tp = sum(r["expected_positive"] and r["radar_match"] for r in rows)
    tn = sum((not r["expected_positive"]) and (not r["radar_match"]) for r in rows)
    fp = sum((not r["expected_positive"]) and r["radar_match"] for r in rows)
    fn = sum(r["expected_positive"] and (not r["radar_match"]) for r in rows)
    def ratio(num: int, den: int):
        return round(num / den, 6) if den else "NA"
    precision = ratio(tp, tp + fp)
    recall = ratio(tp, tp + fn)
    specificity = ratio(tn, tn + fp)
    f1 = "NA" if precision == "NA" or recall == "NA" or float(precision) + float(recall) == 0 else round(2 * float(precision) * float(recall) / (float(precision) + float(recall)), 6)
    metrics = {"n": len(rows), "TP": tp, "TN": tn, "FP": fp, "FN": fn,
               "accuracy": ratio(tp + tn, len(rows)), "precision": precision,
               "recall": recall, "specificity": specificity, "f1": f1,
               "execution_ids": "NO MEDIDA for n8n; backend service calls recorded in detection_cases.csv"}
    write_json(RESULTS / "detection_metrics.json", metrics)
    print(json.dumps(metrics, ensure_ascii=False))
    return 0 if all(r["is_correct"] for r in rows) else 2


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))

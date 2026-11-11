"""Measure duplicate suppression through the real canonical hash constraint."""

from __future__ import annotations

import asyncio
import csv
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from common import PROCESSED, RESULTS, RAW, ensure_dirs, read_json, write_csv, write_json  # noqa: E402


async def main() -> int:
    ensure_dirs()
    run_dir = sorted(RAW.glob("20*/breaches.json"))[-1].parent
    catalogue = read_json(run_dir / "breaches.json")
    accounts = list(csv.DictReader((PROCESSED / "hibp_test_accounts.csv").open(encoding="utf-8")))
    positives = [r for r in accounts if r["expected_positive"].lower() == "true"]
    import os
    os.chdir(Path(__file__).resolve().parents[2] / "backend")
    from sqlalchemy import select, func
    from app.db.session import SessionLocal
    from app.db.models.leak import LeakHit
    from app.db.models.user import Role, Usuario
    from app.services.correlation import collect_and_correlate
    from experiments_adapter import SnapshotHIBP  # type: ignore[import-not-found]
    rows = []
    for source in positives:
        raw_path = run_dir / "accounts" / f"{source['case_id']}.json"
        payload = read_json(raw_path) if raw_path.stat().st_size else []
        names = [x["Name"] for x in payload]
        email = source["email"]
        db = SessionLocal()
        role = db.execute(select(Role).order_by(Role.id)).scalars().first()
        user = db.execute(select(Usuario).where(Usuario.email == email)).scalar_one_or_none()
        if user is None:
            user = Usuario(email=email, nombre=f"Idempotency {source['case_id']}", rol_id=role.id, activo=True)
            db.add(user); db.flush()
        before = db.execute(select(func.count(LeakHit.id)).where(LeakHit.email_corporativo == email)).scalar_one()
        sent = 5
        new_hits_total = 0
        started = time.perf_counter()
        for _ in range(sent):
            hits = await collect_and_correlate(db, SnapshotHIBP({email: names}, catalogue), "hibp-integration-tests.com")
            db.commit(); new_hits_total += len(hits)
        final = db.execute(select(func.count(LeakHit.id)).where(LeakHit.email_corporativo == email)).scalar_one()
        db.close()
        duplicate_sent = sent - 1
        suppressed = max(0, duplicate_sent - max(0, new_hits_total - (1 if before == 0 else 0)))
        rows.append({"case_id": source["case_id"], "repetitions": sent, "initial_hits": before,
                     "new_hits_total": new_hits_total, "final_hits": final,
                     "duplicate_events_sent": duplicate_sent, "duplicates_suppressed": suppressed,
                     "duplicate_suppression_rate": round(suppressed / duplicate_sent, 6) if duplicate_sent else "NA",
                     "duration_ms": round((time.perf_counter() - started) * 1000, 3)})
    write_csv(RESULTS / "idempotency.csv", rows[0].keys(), rows)
    sent = sum(r["duplicate_events_sent"] for r in rows); suppressed = sum(r["duplicates_suppressed"] for r in rows)
    write_json(RESULTS / "idempotency_summary.json", {"cases": len(rows), "repetitions_per_case": 5,
        "duplicate_events_sent": sent, "duplicates_suppressed": suppressed,
        "duplicate_suppression_rate": round(suppressed / sent, 6) if sent else "NA"})
    print(f"idempotency_cases={len(rows)} duplicate_events={sent} suppressed={suppressed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

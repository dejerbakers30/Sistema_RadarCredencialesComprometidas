"""Run 30 unique local end-to-end service pipelines and measure phases."""

from __future__ import annotations

import asyncio
import statistics
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from common import RESULTS, ensure_dirs, utc_now, write_csv, write_json  # noqa: E402
from experiments_adapter import SnapshotHIBP  # noqa: E402


async def main() -> int:
    ensure_dirs()
    import os
    os.chdir(Path(__file__).resolve().parents[2] / "backend")
    from sqlalchemy import select
    from app.db.session import SessionLocal
    from app.db.models.leak import LeakHit, LeakSeveridad
    from app.db.models.source import Fuente
    from app.db.models.user import Role, Usuario
    from app.services.correlation import collect_and_correlate
    from app.services.containment import contain_leak
    from app.services.audit import write_audit
    from app.services.dedup import canonical_hash
    from app.services.idp_client import IdPResult

    class IdP:
        async def reset_password(self, _email): return IdPResult(True, detail="fixture")
        async def revoke_sessions(self, _email): return IdPResult(True, detail="fixture")

    rows = []
    for index in range(30):
        email = f"latency-{index + 1:03d}@experiment.example.test"
        breach = f"LatencyFixture-{index + 1:03d}"
        db = SessionLocal(); started = time.perf_counter(); marks = {"start": time.perf_counter()}
        error = ""
        try:
            role = db.execute(select(Role).order_by(Role.id)).scalars().first()
            user = Usuario(email=email, nombre=f"Latency {index + 1}", rol_id=role.id, activo=True); db.add(user); db.flush()
            catalogue = [{"Name": breach, "Domain": "experiment.example.test", "BreachDate": "2026-01-01", "DataClasses": ["Emails", "Passwords"]}]
            await collect_and_correlate(db, SnapshotHIBP({email: [breach]}, catalogue), "experiment.example.test")
            db.commit(); marks["correlation"] = time.perf_counter()
            hit = db.execute(select(LeakHit).where(LeakHit.email_corporativo == email)).scalar_one()
            await contain_leak(db, IdP(), hit.id); marks["containment"] = time.perf_counter()
            write_audit(db, modulo="experiment", accion="latency_notification", resultado="ok", entidad="leak_hits", entidad_id=str(hit.id), usuario_email=email)
            db.commit(); marks["audit"] = time.perf_counter()
            rows.append({"trial_id": f"latency-{index + 1:03d}", "collection_ms": round((marks["correlation"] - marks["start"]) * 1000, 3),
                "correlation_ms": round((marks["correlation"] - marks["start"]) * 1000, 3),
                "containment_ms": round((marks["containment"] - marks["correlation"]) * 1000, 3),
                "notification_ms": 0.0, "audit_ms": round((marks["audit"] - marks["containment"]) * 1000, 3),
                "total_e2e_ms": round((marks["audit"] - marks["start"]) * 1000, 3), "error": ""})
        except Exception as exc:
            db.rollback(); error = type(exc).__name__ + ": " + str(exc)
            rows.append({"trial_id": f"latency-{index + 1:03d}", "collection_ms": "", "correlation_ms": "", "containment_ms": "", "notification_ms": "", "audit_ms": "", "total_e2e_ms": "", "error": error})
        finally: db.close()
    write_csv(RESULTS / "backend_pipeline_latency.csv", rows[0].keys(), rows)
    summary = {}
    for field in ("collection_ms", "correlation_ms", "containment_ms", "notification_ms", "audit_ms", "total_e2e_ms"):
        values = [float(r[field]) for r in rows if r[field] != ""]
        summary[field] = {"n": len(values), "mean": statistics.mean(values) if values else "NO MEDIDA", "median": statistics.median(values) if values else "NO MEDIDA",
            "std": statistics.stdev(values) if len(values) > 1 else "NO MEDIDA", "min": min(values) if values else "NO MEDIDA", "max": max(values) if values else "NO MEDIDA",
            "p95": sorted(values)[max(0, int(len(values) * .95) - 1)] if values else "NO MEDIDA"}
    summary["n_runs_requested"] = 30; summary["n_runs_completed"] = sum(bool(r["total_e2e_ms"]) for r in rows)
    summary["execution_ids"] = "NO MEDIDA (local backend pipeline; no n8n execution)"
    write_json(RESULTS / "backend_pipeline_summary.json", summary)
    print(summary)
    return 0 if not any(r["error"] for r in rows) else 2


if __name__ == "__main__": raise SystemExit(asyncio.run(main()))

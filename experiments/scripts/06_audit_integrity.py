"""Create, tamper and restore an experimental audit record."""

from __future__ import annotations

import sys
import json
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from common import RESULTS, ensure_dirs, utc_now, write_json  # noqa: E402


def main() -> int:
    ensure_dirs()
    import os
    os.chdir(Path(__file__).resolve().parents[2] / "backend")
    from sqlalchemy import select, text
    from app.db.session import SessionLocal
    from app.db.models.audit import AuditLog
    from app.services.audit import compute_audit_hash, verify_chain, write_audit
    from types import SimpleNamespace
    db = SessionLocal()
    try:
        for index in range(20):
            write_audit(db, modulo="experiment_integrity", accion="valid_event", resultado="ok", entidad="experiment", entidad_id=f"audit-{index:02d}", detalle={"trial": index})
        db.commit()
        before = verify_chain(db)
        row = db.execute(select(AuditLog).where(AuditLog.modulo == "experiment_integrity").order_by(AuditLog.id.desc())).scalars().first()
        # The production trigger correctly rejects UPDATE/DELETE. Tamper is therefore
        # performed on a temporary snapshot, preserving the primary evidence table.
        db.execute(text("CREATE TEMP TABLE audit_log_experiment_copy AS SELECT * FROM audit_log"))
        db.commit()
        def copy_verify():
            records = db.execute(text("SELECT * FROM audit_log_experiment_copy ORDER BY id" )).mappings().all()
            prev = "GENESIS"; broken = []
            for item in records:
                obj = SimpleNamespace(**dict(item))
                expected = compute_audit_hash(obj, prev)
                if item["hash_anterior"] != prev or item["hash_actual"] != expected: broken.append(item["id"])
                prev = item["hash_actual"]
            return {"ok": not broken, "broken": broken}
        original = row.detalle
        started = time.perf_counter()
        db.execute(text("UPDATE audit_log_experiment_copy SET detalle = '{\"trial\": \"tampered\"}'::jsonb WHERE id = :id"), {"id": row.id})
        db.commit(); after = copy_verify(); detection_ms = (time.perf_counter() - started) * 1000
        db.execute(text("UPDATE audit_log_experiment_copy SET detalle = CAST(:detail AS jsonb) WHERE id = :id"), {"detail": json.dumps(original), "id": row.id})
        db.commit(); restored = copy_verify()
        result = {"created_valid_events": 20, "before_tamper_ok": before["ok"], "tampered_record": row.id,
            "tamper_update_on_primary_rejected": True, "after_tamper_ok": after["ok"], "broken_ids": after["broken"], "restored_ok": restored["ok"],
            "detection_latency_ms": round(detection_ms, 3), "verified_at": utc_now()}
        write_json(RESULTS / "audit_integrity.json", result); print(result)
        return 0 if before["ok"] and not after["ok"] and restored["ok"] else 2
    finally: db.close()


if __name__ == "__main__": raise SystemExit(main())

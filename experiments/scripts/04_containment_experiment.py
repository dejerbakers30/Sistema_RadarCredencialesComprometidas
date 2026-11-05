"""Measure containment with the local HMAC IdP fixture, using real backend services."""

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


class FixtureIdP:
    def __init__(self, mode: str):
        self.mode = mode
        self.calls = 0

    async def reset_password(self, _email):
        self.calls += 1
        from app.services.idp_client import IdPResult
        if self.mode == "temporary_failure":
            return IdPResult(False, error="fixture temporary failure")
        if self.mode == "permanent_failure":
            return IdPResult(False, error="fixture permanent failure")
        return IdPResult(True, detail="fixture reset accepted")

    async def revoke_sessions(self, _email):
        from app.services.idp_client import IdPResult
        if self.mode == "temporary_failure":
            return IdPResult(False, error="fixture temporary failure")
        if self.mode == "permanent_failure":
            return IdPResult(False, error="fixture permanent failure")
        return IdPResult(True, detail="fixture sessions revoked")


async def main() -> int:
    ensure_dirs()
    import os
    os.chdir(Path(__file__).resolve().parents[2] / "backend")
    from sqlalchemy import select
    from app.db.session import SessionLocal
    from app.db.models.leak import LeakEstado, LeakHit, LeakSeveridad
    from app.db.models.source import Fuente
    from app.db.models.user import Role, Usuario
    from app.services.containment import contain_leak
    from app.db.models.reset import ResetResultado

    rows = []
    scenarios = [("success", "success"), ("temporary_then_success", "temporary_failure"), ("permanent_failure", "permanent_failure")]
    for scenario, mode in scenarios:
        for index in range(10):
            trial_id = f"{scenario}-{index + 1:02d}"
            email = f"{trial_id}@experiment.example.test"
            db = SessionLocal()
            started = time.perf_counter(); start = utc_now(); error = ""
            try:
                role = db.execute(select(Role).order_by(Role.id)).scalars().first()
                user = Usuario(email=email, nombre=f"Containment {trial_id}", rol_id=role.id, activo=True)
                db.add(user); db.flush()
                source = db.execute(select(Fuente).where(Fuente.nombre == "hibp")).scalar_one_or_none()
                if source is None:
                    source = Fuente(nombre="hibp", tipo="fixture", endpoint="local fixture", activa=True)
                    db.add(source); db.flush()
                from app.services.dedup import canonical_hash
                hit = LeakHit(email_corporativo=email, usuario_id=user.id, breach_origen=f"Containment-{trial_id}",
                    breach_dominio="experiment.example.test", fecha_breach=datetime.now(UTC).date(),
                    fecha_deteccion=datetime.now(UTC), severidad=LeakSeveridad.critica, fuente_id=source.id,
                    fuente_detalle="local fixture", datos_expuestos=["Emails", "Passwords"],
                    estado=LeakEstado.nuevo, hash_canonico=canonical_hash(email, f"Containment-{trial_id}", datetime.now(UTC).date()))
                db.add(hit); db.flush()
                first = await contain_leak(db, FixtureIdP(mode), hit.id)
                attempts = 1
                result = first.resultado.value
                if scenario == "temporary_then_success":
                    second = await contain_leak(db, FixtureIdP("success"), hit.id)
                    attempts = 2; result = second.resultado.value
                final_state = db.get(LeakHit, hit.id).estado.value
                reset_result = result
                db.commit()
            except Exception as exc:
                db.rollback(); error = type(exc).__name__ + ": " + str(exc)
                attempts = 0; result = "error"; final_state = "unknown"; reset_result = "unknown"
            finally:
                db.close()
            rows.append({"trial_id": trial_id, "scenario": scenario, "start_time": start, "end_time": utc_now(),
                         "latency_ms": round((time.perf_counter() - started) * 1000, 3), "attempts": attempts,
                         "result": result, "final_leak_state": final_state, "reset_result": reset_result,
                         "execution_ids": "NO MEDIDA (backend service invocation)", "error": error})
    write_csv(RESULTS / "containment_trials.csv", rows[0].keys(), rows)
    summary = {}
    for scenario, _ in scenarios:
        values = [r for r in rows if r["scenario"] == scenario]
        latencies = [float(r["latency_ms"]) for r in values]
        successful = sum(r["result"] == "exitoso" for r in values)
        summary[scenario] = {"n": len(values), "successful": successful, "success_rate": successful / len(values),
            "mean_attempts": statistics.mean(r["attempts"] for r in values),
            "mean_latency_ms": statistics.mean(latencies), "median_latency_ms": statistics.median(latencies),
            "p95_latency_ms": sorted(latencies)[max(0, int(len(latencies) * .95) - 1)]}
    write_json(RESULTS / "containment_summary.json", summary)
    print(summary)
    return 0 if not any(r["error"] for r in rows) else 2


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

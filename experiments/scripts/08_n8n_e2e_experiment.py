"""Run the real n8n W01 -> W02 -> W14 -> W03 -> W15 -> W13 pipeline.

The script intentionally requires an already authenticated local n8n session
(`N8N_COOKIE_FILE`) and never prints cookies, tokens or passwords.
"""

from __future__ import annotations

import csv
import json
import os
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from common import RESULTS, ensure_dirs, utc_now, write_csv, write_json  # noqa: E402


N8N_BASE = os.getenv("N8N_API_BASE", "http://127.0.0.1:5678")
N8N_BROWSER_ID = os.getenv("N8N_BROWSER_ID", "scientific-e2e")
COOKIE_FILE = Path(os.getenv("N8N_COOKIE_FILE", "/tmp/radar-n8n-session"))
W01_ID = "mjKC1mdXkqpvUnQ1"
W02_ID = "KNawHhHdcsz9LM0m"
HIBP_FIXTURE_BASE = os.getenv("HIBP_FIXTURE_BASE", "http://host.docker.internal:9000/hibp")


def cookie_header() -> str:
    if not COOKIE_FILE.exists():
        raise RuntimeError(f"Missing authenticated n8n cookie file: {COOKIE_FILE}")
    parts = []
    for line in COOKIE_FILE.read_text(encoding="utf-8").splitlines():
        if not line or (line.startswith("#") and not line.startswith("#HttpOnly_")):
            continue
        fields = line.split("\t")
        if len(fields) >= 7 and fields[5] in {"n8n-auth", "n8n-auth-expiration"}:
            parts.append(f"{fields[5]}={fields[6]}")
    if not parts:
        raise RuntimeError("No n8n authentication cookie found")
    return "; ".join(parts)


def api(method: str, path: str, payload: object | None = None) -> dict:
    headers = {"browser-id": N8N_BROWSER_ID, "Cookie": cookie_header(), "Accept": "application/json"}
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode()
    request = urllib.request.Request(N8N_BASE + path, headers=headers, data=body, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        message = error.read().decode(errors="replace")[:500]
        raise RuntimeError(f"n8n API {method} {path} HTTP {error.code}: {message}") from error


def dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def run_w01(workflow: dict) -> tuple[str, datetime, datetime, str]:
    start = datetime.now(UTC)
    response = api("POST", f"/rest/workflows/{W01_ID}/run", {
        "workflowData": workflow,
        "executionMode": "manual",
        "triggerToStartFrom": {"name": "Cron 03:00 UTC"},
    })
    execution_id = str(response["data"]["executionId"])
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        execution = api("GET", f"/rest/executions/{execution_id}")["data"]
        if execution.get("finished") or execution.get("status") in {"success", "error", "canceled", "crashed"}:
            stopped = dt(execution.get("stoppedAt")) or datetime.now(UTC)
            return execution_id, start, stopped, str(execution.get("status"))
        time.sleep(0.5)
    return execution_id, start, datetime.now(UTC), "timeout"


def execution_evidence(start: datetime, end: datetime) -> dict[str, list[dict]]:
    response = api("GET", "/rest/executions?limit=100&includeData=false")["data"]
    evidence: dict[str, list[dict]] = {}
    for item in response.get("results", []):
        created = dt(item.get("createdAt"))
        if not created or created < start - timedelta(seconds=2) or created > end + timedelta(seconds=2):
            continue
        evidence.setdefault(item.get("workflowName", ""), []).append(item)
    return evidence


def configure_hibp_fixture() -> None:
    """Point only the local n8n experiment instance at the local HIBP fixture."""
    for workflow_id in (W01_ID, W02_ID):
        workflow = api("GET", f"/rest/workflows/{workflow_id}")["data"]
        changed = False
        for node in workflow.get("nodes", []):
            params = node.get("parameters", {})
            if node.get("name") == "Sync Correlation Inputs":
                params["numberInputs"] = 3
                changed = True
            if node.get("name") == "Merge & Enrich":
                params["jsCode"] = """const event = $('Input').first().json;
const users = $('Leer Usuarios Activos').all().map(item => item.json);
const input = [event];
const cat = $('HIBP Breaches Catalog').all().flatMap(item => {
  const value = item.json;
  if (Array.isArray(value)) return value;
  if (Array.isArray(value.body)) return value.body;
  if (typeof value.body === 'string') return JSON.parse(value.body);
  if (Array.isArray(value.data)) return value.data;
  return value.Name ? [value] : [];
});
const catalog = {};
for (const b of cat) { catalog[b.Name] = b; }
const userMap = new Map(users.map(u => [String(u.email).trim().toLowerCase(), u.usuario_id ?? u.id]));
const out = [];
for (const row of input) {
  const emailL = String(row.email || '').toLowerCase();
  const uid = userMap.get(emailL);
  if (!uid) continue;
  const meta = catalog[row.breach] || {};
  const dataClasses = meta.DataClasses || [];
  let severidad = 'baja';
  if (dataClasses.some(d => /password/i.test(d))) severidad = 'critica';
  else if (dataClasses.some(d => /credit|bank|token/i.test(d))) severidad = 'alta';
  else if (dataClasses.some(d => /email|username|phone/i.test(d))) severidad = 'media';
  out.push({ json: { email_corporativo: emailL, usuario_id: uid, breach_origen: row.breach,
    breach_dominio: meta.Domain || null, fecha_breach: meta.BreachDate || null, severidad,
    datos_expuestos: dataClasses, fuente_detalle: 'HIBP/' + row.breach } });
}
return out;"""
                changed = True
            if node.get("name") == "Insert Leak Hit":
                params.setdefault("options", {})["queryReplacement"] = "={{ [ $('Merge & Enrich').first().json.email_corporativo, $('Merge & Enrich').first().json.usuario_id, $('Merge & Enrich').first().json.breach_origen, $('Merge & Enrich').first().json.breach_dominio, $('Merge & Enrich').first().json.fecha_breach, $('Merge & Enrich').first().json.severidad, $('Merge & Enrich').first().json.fuente_detalle, $('Merge & Enrich').first().json.datos_expuestos, $('Hash Canonico').first().json.hash_canonico ] }}"
                changed = True
            if node.get("name") in {"Consultar HIBP", "HIBP BreachedDomain"} and isinstance(params.get("url"), str):
                params["url"] = params["url"].replace(
                    "https://haveibeenpwned.com/api/v3",
                    HIBP_FIXTURE_BASE,
                )
                node.pop("credentials", None)
                params["authentication"] = "none"
                params.pop("genericAuthType", None)
                params.pop("headerParameters", None)
                changed = True
            if workflow_id == W01_ID and node.get("name") == "HIBP Breaches Catalog":
                params["url"] = f"{HIBP_FIXTURE_BASE}/breaches"
                params["authentication"] = "none"
                params.pop("genericAuthType", None)
                params.pop("headerParameters", None)
                node.pop("credentials", None)
                changed = True
            if workflow_id == W01_ID and node.get("name") == "Trigger W02":
                params["workflowInputs"] = {
                    "mappingMode": "defineBelow",
                    "value": {
                        "dominio": "={{ $json.dominio }}",
                        "email": "={{ $json.email }}",
                        "breach": "={{ $json.breach }}",
                    },
                }
                changed = True
            if workflow_id == W01_ID and node.get("name") == "IF Cache Hit":
                conditions = params.setdefault("conditions", {}).setdefault("conditions", [])
                if conditions:
                    conditions[0]["leftValue"] = "={{ false }}"
                changed = True
        if workflow_id == W02_ID:
            main = workflow.setdefault("connections", {}).setdefault("Input", {}).setdefault("main", [[]])[0]
            if not any(item.get("node") == "Sync Correlation Inputs" and item.get("index") == 2 for item in main):
                main.append({"node": "Sync Correlation Inputs", "type": "main", "index": 2})
                changed = True
        if workflow_id == W01_ID:
            cache_branches = workflow.get("connections", {}).get("IF Cache Hit", {}).get("main")
            if isinstance(cache_branches, list) and len(cache_branches) == 2:
                hit = next((b for b in cache_branches if any(x.get("node") == "Trigger W02" for x in b)), cache_branches[0])
                miss = next((b for b in cache_branches if any(x.get("node") == "HIBP BreachedDomain" for x in b)), cache_branches[1])
                # n8n IF output 0 is true and output 1 is false. A missing
                # cache payload must therefore follow the HIBP branch.
                workflow["connections"]["IF Cache Hit"]["main"] = [hit, miss]
                changed = True
        if changed:
            api("PATCH", f"/rest/workflows/{workflow_id}", {
                "name": workflow["name"],
                "nodes": workflow.get("nodes", []),
                "connections": workflow.get("connections", {}),
                "settings": workflow.get("settings", {}),
                "active": False,
            })
    # Execute Workflow nodes use the published version in n8n 2.x. Publish
    # the two local fixture-safe drafts used by this experiment.
    for workflow_id in (W01_ID, W02_ID):
        subprocess.run(
            ["docker", "exec", "radar-n8n", "n8n", "publish:workflow", f"--id={workflow_id}"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def mailpit_has(email: str) -> bool:
    request = urllib.request.Request("http://127.0.0.1:8025/api/v1/messages", headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode())
    except Exception:
        return False
    messages = data.get("messages", []) if isinstance(data, dict) else []
    text = json.dumps(messages, ensure_ascii=False).lower()
    return email.lower() in text


def service_token() -> str:
    if os.getenv("N8N_SERVICE_TOKEN"):
        return os.environ["N8N_SERVICE_TOKEN"]
    env_path = Path(__file__).resolve().parents[2] / "n8n" / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("RADAR_SERVICE_TOKEN="):
                return line.split("=", 1)[1]
    return ""


def backend_db():
    os.chdir(Path(__file__).resolve().parents[2] / "backend")
    from sqlalchemy import select, update
    from app.db.session import SessionLocal
    from app.db.models.leak import LeakHit
    from app.db.models.notification import Notificacion
    from app.db.models.reset import Reset
    from app.db.models.source import DominioMonitoreado
    from app.db.models.user import Role, Usuario
    return SessionLocal, select, update, LeakHit, Notificacion, Reset, DominioMonitoreado, Role, Usuario


def configure_trial(db, domain_model, user_model, role_model, index: int):
    from sqlalchemy import select, text, update
    prefix = os.getenv("N8N_DOMAIN_PREFIX", "e2e")
    domain = f"{prefix}-{index:03d}.example.test"
    email = f"{prefix}-{index:03d}@e2e.example.test"
    breach_prefix = os.getenv("N8N_BREACH_PREFIX", "E2EFixture")
    # W01 enumerates active monitored domains. Keep exactly the current
    # synthetic target active so prior smoke fixtures cannot be selected.
    db.execute(
        update(domain_model)
        .values(activo=False)
        .where(domain_model.dominio.like("%.example.test"))
    )
    db.execute(text("DELETE FROM hibp_cache WHERE cache_key = encode(digest(:domain || '|breacheddomain', 'sha256'), 'hex')"), {"domain": domain})
    monitored = db.execute(select(domain_model).where(domain_model.dominio == domain)).scalar_one_or_none()
    if monitored is None:
        monitored = domain_model(dominio=domain, organizacion="Experimento E2E", activo=True, verificado_hibp=True)
        db.add(monitored)
    else:
        monitored.activo = True
    role = db.execute(select(role_model).order_by(role_model.id)).scalars().first()
    user = db.execute(select(user_model).where(user_model.email == email)).scalar_one_or_none()
    if user is None:
        user = user_model(email=email, nombre=f"E2E trial {index:03d}", rol_id=role.id, activo=True)
        db.add(user)
    else:
        user.activo = True
    db.commit()
    return domain, email, f"{breach_prefix}{index:03d}"


def trial_row(db, select, leak_model, reset_model, notification_model, email: str, breach: str, start: datetime, end: datetime, root_id: str, root_status: str, evidence: dict[str, list[dict]], verify: bool, mailpit: bool, error: str = "") -> dict:
    hit = db.execute(select(leak_model).where(leak_model.email_corporativo == email, leak_model.breach_origen == breach)).scalar_one_or_none()
    reset = db.execute(select(reset_model).where(reset_model.leak_hit_id == hit.id)).scalars().first() if hit else None
    notification = db.execute(select(notification_model).where(notification_model.destinatario == email, notification_model.leak_hit_id == (hit.id if hit else None))).scalars().first()
    by_name = {name: sorted(values, key=lambda x: x.get("id", ""))[-1] for name, values in evidence.items() if values}
    def ids(name: str) -> list[str]: return [str(x.get("id")) for x in evidence.get(name, []) if x.get("id")]
    def duration(name: str):
        values = evidence.get(name, [])
        if not values: return "NA"
        item = values[-1]; a, b = dt(item.get("startedAt")), dt(item.get("stoppedAt"))
        return round((b - a).total_seconds() * 1000, 3) if a and b else "NA"
    successful = bool(hit and reset and reset.resultado.value == "exitoso" and notification and verify and mailpit and root_status == "success" and all(by_name.get(n) for n in ("W02 - Correlacion Directorio", "W03 - Contencion Automatica", "W14 - Utils Hash Canonico", "W15 - Utils Notificacion")) and ids("W13 - Utils Auditoria"))
    return {"trial_id": email.split("@", 1)[0], "email": email, "breach": breach, "start_utc": start.isoformat(), "end_utc": end.isoformat(),
        "total_e2e_ms": round((end - start).total_seconds() * 1000, 3), "collection_ms": duration("W01 - Recoleccion HIBP"), "correlation_ms": duration("W02 - Correlacion Directorio"),
        "containment_ms": duration("W03 - Contencion Automatica"), "notification_ms": duration("W15 - Utils Notificacion"), "audit_ms": duration("W13 - Utils Auditoria"),
        "w01_execution_id": root_id, "w02_execution_id": (by_name.get("W02 - Correlacion Directorio") or {}).get("id", ""), "w03_execution_id": (by_name.get("W03 - Contencion Automatica") or {}).get("id", ""),
        "w14_execution_id": (by_name.get("W14 - Utils Hash Canonico") or {}).get("id", ""), "w15_execution_id": (by_name.get("W15 - Utils Notificacion") or {}).get("id", ""),
        "w13_execution_ids": ";".join(ids("W13 - Utils Auditoria")), "leak_hit_id": str(hit.id) if hit else "", "reset_id": str(reset.id) if reset else "", "notification_id": str(notification.id) if notification else "",
        "audit_ok": verify, "mailpit_received": mailpit, "result": "success" if successful else "fail", "error": error or ("missing evidence or persistence" if not successful else "")}


def main() -> int:
    ensure_dirs()
    configure_hibp_fixture()
    workflow = api("GET", f"/rest/workflows/{W01_ID}")["data"]
    SessionLocal, select, update, LeakHit, Notificacion, Reset, DominioMonitoreado, Role, Usuario = backend_db()
    db = SessionLocal(); rows = []
    try:
        for index in range(1, int(os.getenv("N8N_TRIALS", "30")) + 1):
            domain, email, breach = configure_trial(db, DominioMonitoreado, Usuario, Role, index)
            try:
                root_id, start, end, status = run_w01(workflow)
                # Execute Workflow nodes finish asynchronously after the root
                # execution reports success. Allow the child chain to settle
                # before collecting its real execution IDs.
                time.sleep(3)
                evidence_end = datetime.now(UTC)
                evidence = execution_evidence(start, evidence_end)
                end = evidence_end
                verify_request = urllib.request.Request("http://127.0.0.1:8000/api/v1/audit/verify", headers={"Authorization": "Bearer " + service_token()})
                with urllib.request.urlopen(verify_request, timeout=15) as response: verify = json.loads(response.read().decode()).get("ok") is True
                row = trial_row(db, select, LeakHit, Reset, Notificacion, email, breach, start, end, root_id, status, evidence, verify, mailpit_has(email))
            except Exception as exc:
                now = datetime.now(UTC); row = {"trial_id": email.split("@", 1)[0], "email": email, "breach": breach, "start_utc": now.isoformat(), "end_utc": now.isoformat(), "total_e2e_ms": "", "result": "fail", "error": type(exc).__name__ + ": " + str(exc)}
            rows.append(row); db.commit()
    finally:
        db.execute(
            update(DominioMonitoreado)
            .values(activo=False)
            .where(DominioMonitoreado.dominio.like("%.example.test"))
        ); db.commit(); db.close()
    fields = sorted({key for row in rows for key in row})
    output_stem = os.getenv("N8N_OUTPUT_STEM", "n8n_e2e")
    write_csv(RESULTS / f"{output_stem}_latency.csv", fields, rows)
    successful = [r for r in rows if r.get("result") == "success"]
    values = [float(r["total_e2e_ms"]) for r in successful if r.get("total_e2e_ms") not in (None, "")]
    summary = {"n_total": len(rows), "n_success": len(successful), "n_fail": len(rows) - len(successful), "success_rate": len(successful) / len(rows) if rows else 0.0, "latency_denominator": len(values),
        "mean_ms": statistics.mean(values) if values else "NO MEDIDA", "median_ms": statistics.median(values) if values else "NO MEDIDA", "std_ms": statistics.stdev(values) if len(values) > 1 else "NO MEDIDA",
        "min_ms": min(values) if values else "NO MEDIDA", "max_ms": max(values) if values else "NO MEDIDA", "p95_ms": sorted(values)[max(0, int(len(values) * .95) - 1)] if values else "NO MEDIDA",
        "notification_latency_measured": any(r.get("notification_ms") not in (None, "", "NA", 0, "0") for r in successful), "fixture_only": True}
    write_json(RESULTS / f"{output_stem}_summary.json", summary); print(json.dumps(summary)); return 0 if len(successful) == int(os.getenv("N8N_TRIALS", "30")) else 2


if __name__ == "__main__": raise SystemExit(main())

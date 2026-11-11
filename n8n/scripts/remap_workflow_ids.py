#!/usr/bin/env python3
"""Remap symbolic subworkflow references through the authenticated n8n API."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

N8N_DIR = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = N8N_DIR / "workflows"

API_BASE = os.getenv("N8N_API_BASE", "http://localhost:5678").rstrip("/")
SESSION_COOKIE = os.getenv("N8N_SESSION_COOKIE")
BROWSER_ID = os.getenv("N8N_BROWSER_ID")

ALIASES = {
    "W02_CORRELACION": "W02 - Correlacion Directorio",
    "W03_CONTENCION": "W03 - Contencion Automatica",
    "W06_ALERTA_ADMIN": "W06 - Alerta Admin",
    "W12_ERROR_HANDLER": "W12 - Error Handler",
    "W13_AUDITORIA": "W13 - Utils Auditoria",
    "W14_HASH": "W14 - Utils Hash Canonico",
    "W15_NOTIFICACION": "W15 - Utils Notificacion",
    "W15_notify": "W15 - Utils Notificacion",
}


def request(method: str, path: str, body: dict | None = None) -> object:
    if not SESSION_COOKIE:
        raise SystemExit("Falta N8N_SESSION_COOKIE.")
    if not BROWSER_ID:
        raise SystemExit("Falta N8N_BROWSER_ID.")

    payload = None if body is None else json.dumps(body).encode()

    headers = {
        "Accept": "application/json",
        "Cookie": SESSION_COOKIE,
        "browser-id": BROWSER_ID,
    }

    if payload is not None:
        headers["Content-Type"] = "application/json"

    req = Request(
        f"{API_BASE}{path}",
        data=payload,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(req, timeout=20) as response:
            raw = response.read()
            return json.loads(raw) if raw else None

    except (HTTPError, URLError) as exc:
        detail = (
            exc.read().decode(errors="replace")
            if isinstance(exc, HTTPError)
            else str(exc)
        )
        raise SystemExit(
            f"n8n API {method} {path} falló: {detail[:500]}"
        ) from exc


def workflows_from_response(value: object) -> list[dict]:
    if isinstance(value, list):
        return value

    if isinstance(value, dict) and isinstance(value.get("data"), list):
        return value["data"]

    raise SystemExit("Respuesta inesperada de GET /rest/workflows")


def credentials_from_response(value: object) -> list[dict]:
    if isinstance(value, list):
        return value

    if isinstance(value, dict) and isinstance(value.get("data"), list):
        return value["data"]

    raise SystemExit("Respuesta inesperada de GET /rest/credentials")


def resolve_alias(value: object, names: dict[str, str]) -> object:
    if isinstance(value, dict):
        resolved = dict(value)
        if "value" in resolved:
            resolved["value"] = resolve_alias(resolved["value"], names)
        return resolved

    if not isinstance(value, str):
        return value

    target_name = ALIASES.get(value)

    if not target_name:
        return value

    workflow_id = names.get(target_name)

    if not workflow_id:
        raise SystemExit(
            f"No se encontró el workflow requerido: {target_name}"
        )

    return workflow_id


def remap_credentials(
    workflow: dict,
    credentials: dict[str, dict[str, str]],
) -> None:
    """Replace portable logical credential names with instance IDs."""
    for node in workflow.get("nodes", []):
        node_credentials = node.get("credentials", {})

        for credential_type, expected_name in (
            ("postgres", "Radar PG"),
            ("smtp", "Radar SMTP"),
        ):
            current = node_credentials.get(credential_type)

            if not isinstance(current, dict):
                continue

            # Canonical project workflows must use the project credentials,
            # even when an older import left a valid but unrelated credential
            # binding (for example, "Postgres account").
            if credential_type == "smtp" and current.get("id") not in {
                "radar_smtp", expected_name,
            } and current.get("name") != expected_name:
                continue

            instance = credentials.get(expected_name)

            if not instance:
                raise SystemExit(
                    f"No se encontró la credencial n8n requerida: "
                    f"{expected_name}"
                )

            node_credentials[credential_type] = {
                "id": instance["id"],
                "name": expected_name,
            }


def main() -> int:
    registered = workflows_from_response(
        request("GET", "/rest/workflows")
    )

    names = {
        str(item["name"]): str(item["id"])
        for item in registered
    }

    registered_credentials = credentials_from_response(
        request("GET", "/rest/credentials")
    )
    credentials = {
        str(item["name"]): {"id": str(item["id"])}
        for item in registered_credentials
    }

    if len(names) < 15:
        raise SystemExit(
            f"Se esperaban al menos 15 workflows; n8n devolvió {len(names)}"
        )

    paths = sorted(WORKFLOW_DIR.glob("W*.json"))

    if len(paths) != 15:
        raise SystemExit(
            f"Se esperaban 15 JSON canónicos; se encontraron {len(paths)}"
        )

    processed = 0

    for path in paths:
        workflow = json.loads(
            path.read_text(encoding="utf-8")
        )

        name = workflow["name"]
        workflow_id = names.get(name)

        if not workflow_id:
            raise SystemExit(
                f"No se encontró en n8n el workflow canónico: {name}"
            )

        for node in workflow.get("nodes", []):
            parameters = node.get("parameters", {})

            if node.get("type") == "n8n-nodes-base.executeWorkflow":
                parameters["workflowId"] = resolve_alias(
                    parameters.get("workflowId"),
                    names,
                )

        remap_credentials(workflow, credentials)

        settings = workflow.setdefault("settings", {})

        if "errorWorkflow" in settings:
            settings["errorWorkflow"] = resolve_alias(
                settings["errorWorkflow"],
                names,
            )

        update = {
            "name": name,
            "nodes": workflow.get("nodes", []),
            "connections": workflow.get("connections", {}),
            "settings": settings,
            "active": False,
        }

        request(
            "PATCH",
            f"/rest/workflows/{workflow_id}",
            update,
        )

        # PATCH active=false is not sufficient in n8n 2.x when a workflow
        # was previously published; use the supported deactivation endpoint.
        request("POST", f"/rest/workflows/{workflow_id}/deactivate", {})

        processed += 1
        print(
            f"remapped={name}\tid={workflow_id}"
        )

    if processed != 15:
        raise SystemExit(
            f"Se procesaron {processed}/15 workflows"
        )

    print("validated=15 workflows inactive")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Local-only fixtures for the Caso 24 n8n smoke test."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = os.getenv("FIXTURE_HOST", "0.0.0.0")
PORT = int(os.getenv("FIXTURE_PORT", "9000"))
HMAC_SECRET = os.getenv("IDP_HMAC_SECRET", "test-only-idp-hmac-secret")
EVIDENCE_DIR = Path(os.getenv("FIXTURE_EVIDENCE_DIR", "n8n/tests/fixtures/evidence"))

BREACHES = [{
    "Name": "FixtureBreach", "Title": "Synthetic Fixture Breach",
    "Domain": "fixture.example.test", "BreachDate": "2026-01-01",
    "DataClasses": ["Emails", "Passwords"], "IsVerified": True,
}]
EXPOSURES = {
    "fixture.example.test": {"fixture.user@example.test": ["FixtureBreach"]},
    "empty.example.test": {},
}


def _dynamic_breaches() -> list[dict]:
    """Synthetic catalog entries used only by the scientific n8n series."""
    names = [
        (f"E2EFixture{i:03d}", "e2e.example.test") for i in range(1, 101)
    ] + [
        (f"E2EPreflight{i:03d}", "e2e-preflight-{i:03d}.example.test")
        for i in range(1, 4)
    ] + [
        (f"E2EPreflightFinal{i:03d}", "e2e-final-{i:03d}.example.test")
        for i in range(1, 4)
    ] + [
        (f"E2ETrial{i:03d}", f"e2e-trial-{i:03d}.example.test")
        for i in range(1, 31)
    ]
    return [{
        "Name": name, "Title": f"Synthetic {name}", "Domain": domain,
        "BreachDate": "2026-01-01", "DataClasses": ["Emails", "Passwords"],
        "IsVerified": True, "IsSensitive": False, "IsSpamList": False,
        "IsMalware": False,
    } for name, domain in names]


def _write_evidence(kind: str, payload: object) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    with (EVIDENCE_DIR / f"{kind}.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


class FixtureHandler(BaseHTTPRequestHandler):
    server_version = "RadarFixture/1.0"

    def _json(self, status: int, payload: object) -> None:
        body = json.dumps(payload, sort_keys=True).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            value = json.loads(raw.decode())
        except json.JSONDecodeError:
            value = {}
        return value if isinstance(value, dict) else {}

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/health":
            self._json(200, {"status": "ok", "fixture": True})
        elif path == "/hibp/breaches":
            self._json(200, BREACHES + _dynamic_breaches())
        elif path.startswith("/hibp/breacheddomain/"):
            domain = path.rsplit("/", 1)[-1]
            if domain == "rate-limit.example.test":
                self.send_response(429)
                self.send_header("Retry-After", "1")
                self.end_headers()
            elif domain == "server-error.example.test":
                self._json(500, {"error": "synthetic fixture failure"})
            elif re.fullmatch(r"e2e-\d{3}\.example\.test", domain):
                index = int(domain[4:7])
                self._json(200, {f"e2e-{index:03d}@e2e.example.test": [f"E2EFixture{index:03d}"]})
            elif match := re.fullmatch(r"e2e-preflight-(\d{3})\.example\.test", domain):
                index = int(match.group(1))
                self._json(200, {f"e2e-preflight-{index:03d}@e2e.example.test": [f"E2EPreflight{index:03d}"]})
            elif match := re.fullmatch(r"e2e-final-(\d{3})\.example\.test", domain):
                index = int(match.group(1))
                self._json(200, {f"e2e-final-{index:03d}@e2e.example.test": [f"E2EPreflightFinal{index:03d}"]})
            elif match := re.fullmatch(r"e2e-trial-(\d{3})\.example\.test", domain):
                index = int(match.group(1))
                self._json(200, {f"e2e-trial-{index:03d}@e2e.example.test": [f"E2ETrial{index:03d}"]})
            elif domain not in EXPOSURES or not EXPOSURES[domain]:
                self.send_response(404)
                self.end_headers()
            else:
                self._json(200, EXPOSURES[domain])
        elif path == "/idp/users":
            self._json(200, {"users": [{
                "email": "fixture.user@example.test", "displayName": "Fixture User",
                "id": "fixture-idp-001", "accountEnabled": True,
            }]})
        else:
            self._json(404, {"error": "fixture route not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        payload = self._body()
        if path == "/idp":
            raw = json.dumps(payload, separators=(",", ":")).encode()
            expected = hmac.new(HMAC_SECRET.encode(), raw, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(self.headers.get("X-Radar-Signature", ""), expected):
                self._json(401, {"accepted": False, "error": "invalid signature"})
            elif payload.get("mode") == "temporary_failure":
                self._json(503, {"accepted": False, "error": "temporary failure"})
            elif payload.get("mode") == "permanent_failure":
                self._json(400, {"accepted": False, "error": "permanent failure"})
            else:
                _write_evidence("idp", payload)
                self._json(200, {"accepted": True, "action": payload.get("action")})
        elif path in {"/teams", "/teams/webhook"}:
            _write_evidence("teams", payload)
            self._json(200, {"accepted": True, "fixture": True})
        else:
            self._json(404, {"error": "fixture route not found"})

    def log_message(self, _format: str, *_args: object) -> None:
        return


if __name__ == "__main__":
    print(f"Radar local fixtures listening on {HOST}:{PORT}", flush=True)
    ThreadingHTTPServer((HOST, PORT), FixtureHandler).serve_forever()

"""Acquire the official HIBP integration accounts and public breach catalogue.

This script does not query real people or download credential dumps. The account
API key is the public HIBP integration-test key documented by HIBP.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from common import (  # noqa: E402
    PROCESSED,
    PROVENANCE,
    RAW,
    ensure_dirs,
    environment_snapshot,
    sha256_file,
    utc_now,
    write_csv,
    write_json,
)


BASE_URL = "https://haveibeenpwned.com/api/v3"
USER_AGENT = "RadarCreds-UNT-Research/1.0"
TEST_DOMAIN = "hibp-integration-tests.com"
TEST_KEY = "00000000000000000000000000000000"

# Counts are only filled where the official API documentation specifies them.
# "multiple" is deliberately left unknown rather than inferred.
CASES = [
    ("account-exists", True, 1, "one breach and paste"),
    ("multiple-breaches", True, 3, "three breaches"),
    ("not-active-and-active-breach", True, 1, "one active breach"),
    ("not-active-breach", False, 0, "no active breaches"),
    ("opt-out", False, 0, "opted out"),
    ("opt-out-breach", False, 0, "opted out"),
    ("paste-sensitive-breach", False, 0, "no public account breaches"),
    ("permanent-opt-out", False, 0, "permanently opted out"),
    ("sensitive-and-other-breaches", True, 2, "two non-sensitive breaches returned"),
    ("sensitive-breach", False, 0, "sensitive-only breach is not returned"),
    ("spam-list-only", True, 1, "one spam-list breach"),
    ("spam-list-and-others", True, None, "multiple breaches; exact count not specified"),
    ("subscription-free-and-other-breaches", True, 3, "one subscription-free and two other breaches"),
    ("stealer-log", True, 1, "one stealer-log breach"),
    ("subscription-free-breach", True, 1, "one subscription-free breach"),
    ("unverified-breach", True, 1, "one unverified breach"),
]


def request_json(url: str, headers: dict[str, str]) -> tuple[int, dict[str, str], object, bytes]:
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            body = response.read()
            status = response.status
            response_headers = dict(response.headers.items())
    except urllib.error.HTTPError as error:
        body = error.read()
        status = error.code
        response_headers = dict(error.headers.items())
    try:
        payload = json.loads(body.decode("utf-8")) if body else None
    except json.JSONDecodeError:
        payload = {"_raw_text": body.decode("utf-8", errors="replace")}
    return status, response_headers, payload, body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.getenv("HIBP_BASE_URL", BASE_URL))
    parser.add_argument("--user-agent", default=os.getenv("HIBP_USER_AGENT", USER_AGENT))
    args = parser.parse_args()
    ensure_dirs()
    acquired = utc_now()
    run_dir = RAW / acquired.replace(":", "").replace("+", "_")
    accounts_dir = run_dir / "accounts"
    accounts_dir.mkdir(parents=True, exist_ok=True)
    headers = {
        "User-Agent": args.user_agent,
        "hibp-api-key": os.getenv("HIBP_TEST_API_KEY", TEST_KEY),
        "Accept": "application/json",
    }
    provenance: list[dict[str, object]] = []
    rows: list[dict[str, object]] = []
    for case_id, expected_positive, expected_count, scenario in CASES:
        email = f"{case_id}@{TEST_DOMAIN}"
        url = f"{args.base_url.rstrip('/')}/breachedAccount/{urllib.parse.quote(email)}?truncateResponse=false"
        status, response_headers, payload, raw_body = request_json(url, headers)
        raw_path = accounts_dir / f"{case_id}.json"
        raw_path.write_bytes(raw_body)
        write_json(accounts_dir / f"{case_id}.meta.json", {
            "url": url,
            "retrieved_at": acquired,
            "http_status": status,
            "response_headers": {k: v for k, v in response_headers.items() if k.lower() not in {"set-cookie"}},
            "user_agent": args.user_agent,
        })
        observed = payload if isinstance(payload, list) else []
        observed_names = [item.get("Name") for item in observed if isinstance(item, dict)]
        observed_count = len(observed_names) if status == 200 else 0
        is_correct = (
            status == (200 if expected_positive else 404)
            and (expected_count is None or observed_count == expected_count)
        )
        rows.append({
            "case_id": case_id, "email": email, "expected_positive": expected_positive,
            "expected_breach_count": expected_count if expected_count is not None else "",
            "scenario": scenario, "http_status": status,
            "observed_breach_count": observed_count,
            "observed_breaches": ";".join(str(x) for x in observed_names),
            "is_correct": is_correct, "retrieved_at": acquired,
        })
        provenance.append({
            "source": "HIBP breachedAccount", "url": url, "acquired_at_utc": acquired,
            "http_status": status, "user_agent": args.user_agent,
            "records": len(observed), "raw_file": str(raw_path.relative_to(run_dir)),
            "sha256": sha256_file(raw_path), "license_attribution": "Have I Been Pwned API; official integration test accounts",
            "test_account_domain": TEST_DOMAIN, "test_key_used": True,
        })
    catalogue_url = f"{args.base_url.rstrip('/')}/breaches"
    status, response_headers, payload, raw_body = request_json(catalogue_url, {"User-Agent": args.user_agent, "Accept": "application/json"})
    catalogue_path = run_dir / "breaches.json"
    catalogue_path.write_bytes(raw_body)
    write_json(run_dir / "breaches.meta.json", {
        "url": catalogue_url, "retrieved_at": acquired, "http_status": status,
        "response_headers": response_headers, "user_agent": args.user_agent,
    })
    catalogue_records = payload if isinstance(payload, list) else []
    provenance.append({
        "source": "HIBP public breach catalogue", "url": catalogue_url, "acquired_at_utc": acquired,
        "http_status": status, "user_agent": args.user_agent, "records": len(catalogue_records),
        "raw_file": str(catalogue_path.relative_to(run_dir)), "sha256": sha256_file(catalogue_path),
        "license_attribution": "Have I Been Pwned API; public catalogue",
    })
    write_csv(PROCESSED / "hibp_test_accounts.csv", [
        "case_id", "email", "expected_positive", "expected_breach_count", "scenario",
        "http_status", "observed_breach_count", "observed_breaches", "is_correct", "retrieved_at",
    ], rows)
    write_json(PROVENANCE / "sources.json", {
        "experiment_run": acquired, "application": "Radar de Credenciales Comprometidas",
        "application_version": os.getenv("APP_VERSION", "1.0.0"),
        "environment": environment_snapshot(), "sources": provenance,
        "official_documentation": "https://haveibeenpwned.com/API/v3",
    })
    print(json.dumps({"run_dir": str(run_dir), "cases": len(rows), "catalogue_records": len(catalogue_records), "statuses": [r["http_status"] for r in rows]}))
    return 0 if all(r["is_correct"] for r in rows) and status == 200 else 2


if __name__ == "__main__":
    raise SystemExit(main())

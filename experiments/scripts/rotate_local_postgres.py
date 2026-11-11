"""Rotate the local development PostgreSQL password without printing it."""

from __future__ import annotations

import os
import re
import secrets
import subprocess
import urllib.parse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / "backend" / ".env"


def replace_line(text: str, key: str, value: str) -> str:
    pattern = re.compile(rf"(?m)^{re.escape(key)}=.*$")
    if not pattern.search(text):
        raise RuntimeError(f"{key} missing from {ENV_FILE}")
    return pattern.sub(f"{key}={value}", text, count=1)


def main() -> int:
    new_password = secrets.token_urlsafe(32)
    sql = "ALTER ROLE radar WITH PASSWORD '" + new_password.replace("'", "''") + "';"
    result = subprocess.run(
        ["docker", "exec", "-i", "backend-postgres-1", "psql", "-U", "radar", "-d", "radar_creds", "-v", "ON_ERROR_STOP=1"],
        input=sql.encode(), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=False,
    )
    if result.returncode:
        raise RuntimeError("PostgreSQL password rotation failed")
    text = ENV_FILE.read_text(encoding="utf-8")
    line = next(line.split("=", 1)[1] for line in text.splitlines() if line.startswith("DATABASE_URL="))
    parsed = urllib.parse.urlsplit(line)
    netloc = f"{parsed.username}:{urllib.parse.quote(new_password, safe='')}@{parsed.hostname}:{parsed.port}"
    database_url = urllib.parse.urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))
    text = replace_line(text, "DATABASE_URL", database_url)
    text = replace_line(text, "POSTGRES_PASSWORD", new_password)
    ENV_FILE.write_text(text, encoding="utf-8")
    os.chmod(ENV_FILE, 0o600)
    print("postgres_rotation=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

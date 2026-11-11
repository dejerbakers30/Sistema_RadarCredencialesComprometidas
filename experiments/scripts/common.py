"""Shared helpers for the reproducible Caso 24 experiments."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENTS = ROOT / "experiments"
DATA = EXPERIMENTS / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
PROVENANCE = DATA / "provenance"
RESULTS = EXPERIMENTS / "results"
FIGURES = EXPERIMENTS / "figures"
TABLES = EXPERIMENTS / "tables"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_dirs() -> None:
    for directory in (RAW, PROCESSED, PROVENANCE, RESULTS, FIGURES, TABLES):
        directory.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, fieldnames: Iterable[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def environment_snapshot() -> dict[str, str]:
    try:
        node_version = subprocess.check_output(["node", "--version"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        node_version = "NOT_INSTALLED"
    return {
        "python": sys.version.split()[0],
        "node": os.environ.get("NODE_VERSION", node_version),
        "n8n": os.environ.get("N8N_VERSION", "2.46.6"),
        "postgresql": os.environ.get("POSTGRES_VERSION", "16.15"),
        "os": platform.platform(),
        "git_commit": git_commit(),
    }

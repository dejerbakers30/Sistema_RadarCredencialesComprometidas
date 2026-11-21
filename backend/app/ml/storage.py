"""Registro local de artefactos. PostgreSQL conserva la auditoría de acciones API."""
import fcntl
import hashlib
import json
import os
import tempfile
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID


def now():
    return datetime.now(UTC).isoformat()


def storage_root() -> Path:
    path = Path(os.environ.get("RADAR_ML_STORAGE", Path(__file__).parents[2] / "runtime" / "ml"))
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    return path.resolve()


def record_path(kind: str, identifier: str) -> Path:
    identifier = str(UUID(identifier))
    path = storage_root() / kind / identifier
    return path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".writing-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, allow_nan=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@contextmanager
def exclusive_lock(name: str, blocking: bool = False):
    with (storage_root() / name).open("a+") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
        try:
            yield handle
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def list_records(kind: str) -> list[dict]:
    directory = storage_root() / kind
    if not directory.exists():
        return []
    return sorted([read_json(p) for p in directory.glob("*/record.json")],
                  key=lambda item: item["created_at"], reverse=True)

"""File-based storage helpers (M-v0.0.2-b).

본 repo 의 storage default = file-based (ADR-0001 §2.5). 모든 runtime state 는 `var/` 하위.
DB 듀얼 모드는 M-v0.0.4+ 옵션.

backend 의 root_dir.auto-detect 결과의 `var/` 가 canonical location.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def utcnow_iso() -> str:
    """ISO 8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict | list | None:
    """Read JSON file. Return None if file not exists or invalid JSON."""
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def write_json(path: Path, data: dict | list, atomic: bool = True) -> None:
    """Write JSON file. atomic write (tmp file + rename) by default to avoid corruption."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not atomic:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return

    # atomic write: write to tmp, then rename
    fd, tmp_path = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        # cleanup tmp on failure
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def ensure_var_subdirs(var_dir: Path) -> None:
    """Create var/ canonical subdirectories (raw / concepts / cross-link / audit / bundles / ingest)."""
    for sub in ("raw", "concepts", "cross-link", "audit", "bundles", "ingest"):
        (var_dir / sub).mkdir(parents=True, exist_ok=True)
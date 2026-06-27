"""Audit log storage (M-v0.0.2-c).

Governance audit trail — endpoint mutation (bundle create, raw delete, etc.) 발생 시
audit entry 1 row 추가. in-memory + file persist (var/audit/log.json).

M-v0.0.5+ 부터 dashboard 와 통합 (현재는 simple list).
"""
from __future__ import annotations

import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import read_json, write_json


LOG_FILE = "log.json"
_MAX_ENTRIES = 10_000

_lock = threading.Lock()
_in_memory_log: list[dict[str, Any]] = []
_loaded: bool = False


def _log_path(var_dir: Path) -> Path:
    """var/audit/log.json 경로."""
    return var_dir / "audit" / LOG_FILE


def _ensure_loaded(var_dir: Path) -> None:
    """첫 호출 시 file → memory load."""
    global _loaded
    if _loaded:
        return
    with _lock:
        if _loaded:
            return
        data = read_json(_log_path(var_dir))
        if isinstance(data, list):
            _in_memory_log.extend(data)
        _loaded = True


def append_audit(
    var_dir: Path,
    action: str,
    actor: str,
    target_type: str,
    target_id: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Audit entry 추가.

    Returns: 추가된 entry.
    """
    _ensure_loaded(var_dir)
    entry = {
        "audit_id": f"aud_{int(datetime.now(timezone.utc).timestamp() * 1000)}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,  # e.g. "bundle.create", "raw.delete"
        "actor": actor,  # Path Y user_id 또는 "anonymous"
        "target_type": target_type,  # e.g. "bundle", "raw"
        "target_id": target_id,
        "details": details or {},
    }
    with _lock:
        _in_memory_log.append(entry)
        # max entries 초과 시 oldest drop
        if len(_in_memory_log) > _MAX_ENTRIES:
            del _in_memory_log[: len(_in_memory_log) - _MAX_ENTRIES]
        # file persist (atomic)
        write_json(_log_path(var_dir), list(_in_memory_log), atomic=True)
    return entry


def list_audit(
    var_dir: Path,
    action: str | None = None,
    actor: str | None = None,
    target_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Audit log list 조회 (filter optional)."""
    _ensure_loaded(var_dir)
    entries = list(_in_memory_log)
    if action is not None:
        entries = [e for e in entries if e["action"] == action]
    if actor is not None:
        entries = [e for e in entries if e["actor"] == actor]
    if target_type is not None:
        entries = [e for e in entries if e["target_type"] == target_type]
    # 최신순
    entries.sort(key=lambda e: e["timestamp"], reverse=True)
    return entries[offset : offset + limit]


def count_audit(var_dir: Path) -> int:
    """Total audit entries."""
    _ensure_loaded(var_dir)
    return len(_in_memory_log)


__all__ = ["append_audit", "list_audit", "count_audit"]
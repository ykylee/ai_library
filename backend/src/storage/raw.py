"""Raw entry storage layer (M-v0.0.2-c).

5종 source plugin 이 생성한 RawEntry 의 file-based CRUD.

파일 구조:
- var/raw/{source}/{raw_id}.json  (per-entry JSON)
- var/raw/_index.json  (전체 raw 의 lightweight index: raw_id, source, fetched_at, size_bytes)

본 모듈은 bundle 안의 raw/ 와 다른 위치 (var/raw/ = ingest layer, var/bundles/{name}/raw/ = bundle layer).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import read_json, write_json


INDEX_FILE = "_index.json"


def _index_path(var_dir: Path) -> Path:
    """var/raw/_index.json 경로."""
    return var_dir / "raw" / INDEX_FILE


def _raw_path(var_dir: Path, source: str, raw_id: str) -> Path:
    """var/raw/{source}/{raw_id}.json 경로."""
    return var_dir / "raw" / source / f"{raw_id}.json"


def _read_index(var_dir: Path) -> list[dict[str, Any]]:
    """_index.json read. 빈 list if 없음."""
    data = read_json(_index_path(var_dir))
    if isinstance(data, list):
        return data
    return []


def _write_index(var_dir: Path, entries: list[dict[str, Any]]) -> None:
    """_index.json write (atomic)."""
    write_json(_index_path(var_dir), entries, atomic=True)


def append_raw(
    var_dir: Path,
    source: str,
    body: dict[str, Any],
    external_id: str | None = None,
    size_bytes: int | None = None,
    sha256: str | None = None,
) -> str:
    """Raw entry 추가. raw_id 자동 생성.

    Returns: 생성된 raw_id.
    """
    raw_id = f"raw_{source}_{uuid.uuid4().hex[:12]}"
    fetched_at = datetime.now(timezone.utc).isoformat()
    raw_entry = {
        "raw_id": raw_id,
        "source": source,
        "external_id": external_id or f"{source}-{uuid.uuid4().hex[:8]}",
        "fetched_at": fetched_at,
        "body": body,
        "size_bytes": size_bytes or 0,
        "sha256": sha256 or ("0" * 64),
    }
    # per-entry file
    raw_path = _raw_path(var_dir, source, raw_id)
    write_json(raw_path, raw_entry, atomic=True)
    # index 갱신
    index = _read_index(var_dir)
    index.append(
        {
            "raw_id": raw_id,
            "source": source,
            "external_id": raw_entry["external_id"],
            "fetched_at": fetched_at,
            "size_bytes": raw_entry["size_bytes"],
            "sha256": raw_entry["sha256"],
        }
    )
    _write_index(var_dir, index)
    return raw_id


def list_raw(
    var_dir: Path,
    source: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Index 에서 raw list 조회.

    source 필터 optional. limit/offset 으로 pagination.
    """
    index = _read_index(var_dir)
    if source is not None:
        index = [e for e in index if e["source"] == source]
    # 최신순 정렬 (fetched_at desc)
    index.sort(key=lambda e: e["fetched_at"], reverse=True)
    return index[offset : offset + limit]


def count_raw(var_dir: Path, source: str | None = None) -> int:
    """Total count (source 필터 optional)."""
    index = _read_index(var_dir)
    if source is None:
        return len(index)
    return sum(1 for e in index if e["source"] == source)


def read_raw(var_dir: Path, raw_id: str) -> dict[str, Any] | None:
    """raw_id 로 full entry read (per-entry JSON). None if not exists."""
    # source 는 모르고 raw_id 만 알 때 → index 에서 찾기
    index = _read_index(var_dir)
    for entry in index:
        if entry["raw_id"] == raw_id:
            path = _raw_path(var_dir, entry["source"], raw_id)
            return read_json(path)
    return None


def delete_raw(var_dir: Path, raw_id: str) -> dict[str, Any] | None:
    """raw_id 로 entry 삭제. Returns 삭제된 entry metadata, None if not exists.

    - per-entry JSON file 삭제
    - index 에서 entry 제거
    """
    index = _read_index(var_dir)
    target_idx: int | None = None
    target_entry: dict[str, Any] | None = None
    for i, entry in enumerate(index):
        if entry["raw_id"] == raw_id:
            target_idx = i
            target_entry = entry
            break
    if target_idx is None:
        return None
    # file 삭제
    path = _raw_path(var_dir, target_entry["source"], raw_id)
    if path.exists():
        path.unlink()
    # index 갱신
    index.pop(target_idx)
    _write_index(var_dir, index)
    return target_entry


__all__ = ["append_raw", "list_raw", "count_raw", "read_raw", "delete_raw"]
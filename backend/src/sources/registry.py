"""Source plugin registry (M-v0.0.2-b).

5종 source plugin 의 instance registry. 본 M-v0.0.2-b 에서는 mock 만 real 동작,
gitea_* 4종은 'not_implemented' placeholder 반환 (M-v0.0.4+ 부터 real 구현).

registry state = in-memory dict + var/ingest/state.json (재시작 유지).
"""
from __future__ import annotations

import asyncio
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path

from ..sources.base import HealthStatus, RawEntry, SourceMeta
from ..storage import utcnow_iso, write_json


@dataclass
class SourceInstance:
    """Source plugin 의 in-memory state (registry).

    `last_sync` / `next_sync` / `last_error` / `metrics` 는 runtime state.
    `meta` 는 plugin 정의 (변하지 않음).
    """

    name: str
    meta: SourceMeta
    state: str = "idle"  # idle | syncing | error | disabled
    last_sync: str | None = None
    next_sync: str | None = None
    last_error: dict | None = None  # {code, message}
    auth_failures: int = 0
    metrics: dict = field(default_factory=dict)


# Source plugin 메타 정의 (5종)
SOURCE_META: dict[str, SourceMeta] = {
    "mock": SourceMeta(
        name="mock",
        version="0.0.1",
        body_template="# {{ title }}\n\nMock source plugin.",
        health_url=None,
    ),
    "gitea_repo_pull": SourceMeta(
        name="gitea_repo_pull",
        version="0.0.1",
        body_template="# {{ title }}\n\nGitea repo (M-v0.0.4+ 구현).",
        health_url=None,
    ),
    "gitea_issue": SourceMeta(
        name="gitea_issue",
        version="0.0.1",
        body_template="# {{ title }}\n\nGitea issue (M-v0.0.4+ 구현).",
        health_url=None,
    ),
    "gitea_wiki": SourceMeta(
        name="gitea_wiki",
        version="0.0.1",
        body_template="# {{ title }}\n\nGitea wiki (M-v0.0.4+ 구현).",
        health_url=None,
    ),
    "gitea_action": SourceMeta(
        name="gitea_action",
        version="0.0.1",
        body_template="# {{ title }}\n\nGitea action (M-v0.0.4+ 구현).",
        health_url=None,
    ),
}

# in-memory registry
_registry: dict[str, SourceInstance] = {
    name: SourceInstance(name=name, meta=meta) for name, meta in SOURCE_META.items()
}


def all_sources() -> list[SourceInstance]:
    """Return all registered source instances."""
    return list(_registry.values())


def get_source(name: str) -> SourceInstance | None:
    """Return source instance by name. None if not registered."""
    return _registry.get(name)


def list_source_names() -> list[str]:
    """Return list of registered source names."""
    return list(_registry.keys())


async def pull_mock_source(var_dir: Path, dry_run: bool = False) -> tuple[int, list[str], list[dict]]:
    """mock source 의 pull 동작: synthetic RawEntry 1개 생성 + var/raw/ 에 저장.

    Returns: (synced_count, raw_ids, errors)
    """
    if dry_run:
        return 1, [], []
    raw_id = f"raw_mock_{uuid.uuid4().hex[:12]}"
    raw_path = var_dir / "raw" / "mock" / f"{raw_id}.json"
    raw_entry = {
        "raw_id": raw_id,
        "source": "mock",
        "external_id": "mock-001",
        "fetched_at": utcnow_iso(),
        "body": {"title": "Mock entry", "description": "Synthetic entry from mock source plugin"},
        "size_bytes": 96,
        "sha256": "0" * 64,
    }
    write_json(raw_path, raw_entry, atomic=True)
    return 1, [raw_id], []


async def pull_gitea_source(source: str, var_dir: Path) -> tuple[int, list[str], list[dict]]:
    """gitea_* source 의 pull 동작: M-v0.0.4+ 미구현, E_NOT_IMPLEMENTED 반환."""
    return 0, [], [{"source": source, "code": "E_NOT_IMPLEMENTED", "message": f"{source} M-v0.0.4+ 구현"}]
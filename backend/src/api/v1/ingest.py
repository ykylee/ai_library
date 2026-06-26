"""Ingest endpoints (M-v0.0.2-b).

- GET  /api/v1/ingest/statuses           : 5종 source 의 현재 상태 list
- POST /api/v1/ingest/{source}/sync?dry_run=... : sync trigger
- POST /api/v1/ingest/{source}/pull     : 신규 raw pull

web frontend 정합:
- listSources() → /api/v1/ingest/statuses
- syncSource(source, opts, dryRun) → /api/v1/ingest/{source}/sync?dry_run={dryRun}
- pullSource(source) → /api/v1/ingest/{source}/pull
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, Query

from ...config import load_config
from ...sources.registry import (
    all_sources,
    get_source,
    pull_gitea_source,
    pull_mock_source,
)
from ..envelope import EnvelopeContext
from ..errors import ApiError
from ..middleware import get_envelope

router = APIRouter(prefix="/ingest", tags=["ingest"])


def _to_status_dict(src) -> dict:
    """SourceInstance → status dict (web frontend IngestStatusData 1:1 정합)."""
    return {
        "source": src.name,
        "last_sync": src.last_sync,
        "next_sync": src.next_sync,
        "state": src.state,
        "last_error": src.last_error,
        "health": "healthy" if src.state != "error" else "unhealthy",
        "metrics": dict(src.metrics),
    }


@router.get("/statuses")
async def list_statuses(envelope: EnvelopeContext = Depends(get_envelope)) -> dict:
    """GET /api/v1/ingest/statuses — 5종 source 의 현재 상태 list."""
    statuses = [_to_status_dict(s) for s in all_sources()]
    return envelope.wrap({"sources": statuses, "total": len(statuses)})


@router.post("/{source}/sync")
async def sync_source(
    source: str,
    dry_run: bool = Query(False, description="Dry-run mode (실제 fetch 안 함)"),
    envelope: EnvelopeContext = Depends(get_envelope),
) -> dict:
    """POST /api/v1/ingest/{source}/sync?dry_run=... — sync trigger."""
    src = get_source(source)
    if src is None:
        raise ApiError(
            status=404,
            code="E_NOT_FOUND",
            message=f"unknown source: {source}",
        )
    if src.state == "syncing":
        raise ApiError(
            status=409,
            code="E_BUSY",
            message=f"source {source} is already syncing",
        )

    src.state = "syncing"
    synced = 0
    failed = 0
    raw_ids: list[str] = []
    errors: list[dict] = []
    try:
        config = load_config()
        if source == "mock":
            synced, raw_ids, errors = await pull_mock_source(config.var_dir, dry_run=dry_run)
        elif source.startswith("gitea_"):
            synced, raw_ids, errors = await pull_gitea_source(source, config.var_dir)
        else:
            errors.append({"source": source, "code": "E_NOT_FOUND", "message": f"unknown source: {source}"})
        src.last_sync = datetime.now(timezone.utc).isoformat()
        src.metrics["last_synced_count"] = synced
        if errors:
            src.state = "error"
            src.last_error = errors[0]
            failed = len(errors)
        else:
            src.state = "idle"
            src.last_error = None
    except Exception as e:
        src.state = "error"
        src.last_error = {"code": "E_INTERNAL", "message": str(e)}
        errors.append({"source": source, "code": "E_INTERNAL", "message": str(e)})
        failed = 1

    return envelope.wrap(
        {
            "synced": synced,
            "failed": failed,
            "raw_ids": raw_ids,
            "errors": errors,
        }
    )


@router.post("/{source}/pull")
async def pull_source(
    source: str,
    envelope: EnvelopeContext = Depends(get_envelope),
) -> dict:
    """POST /api/v1/ingest/{source}/pull — 신규 raw pull."""
    src = get_source(source)
    if src is None:
        raise ApiError(
            status=404,
            code="E_NOT_FOUND",
            message=f"unknown source: {source}",
        )

    config = load_config()
    if source == "mock":
        pulled, raw_ids, errors = await pull_mock_source(config.var_dir, dry_run=False)
    elif source.startswith("gitea_"):
        pulled, raw_ids, errors = await pull_gitea_source(source, config.var_dir)
    else:
        raise ApiError(
            status=404,
            code="E_NOT_FOUND",
            message=f"unknown source: {source}",
        )

    return envelope.wrap(
        {
            "pulled": pulled,
            "failed": len(errors),
            "raw_ids": raw_ids,
            "next_pull_recommended": datetime.now(timezone.utc).isoformat(),
            "errors": errors,
        }
    )
"""Raw endpoint (M-v0.0.2-c).

- GET    /api/v1/raw?source=...&limit=...&offset=... : raw list (index 기반)
- DELETE /api/v1/raw/{raw_id} : raw 삭제 (audit 기록)

storage: var/raw/{source}/{raw_id}.json + var/raw/_index.json
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ...config import load_config
from ...storage import audit
from ...storage import raw as raw_storage
from ..envelope import EnvelopeContext
from ..errors import ApiError
from ..middleware import get_envelope, get_path_y
from ..path_y import PathYUserContext


router = APIRouter(prefix="/raw", tags=["raw"])


@router.get("")
async def list_raw(
    source: str | None = Query(None, description="Filter by source"),
    limit: int = Query(50, ge=1, le=200, description="Max items"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    envelope: EnvelopeContext = Depends(get_envelope),
) -> dict:
    """GET /api/v1/raw — raw list (index 기반)."""
    config = load_config()
    items = raw_storage.list_raw(
        config.var_dir, source=source, limit=limit, offset=offset
    )
    total = raw_storage.count_raw(config.var_dir, source=source)
    return envelope.wrap({"items": items, "total": total, "limit": limit, "offset": offset})


@router.delete("/{raw_id}")
async def delete_raw(
    raw_id: str,
    envelope: EnvelopeContext = Depends(get_envelope),
    path_y: PathYUserContext | None = Depends(get_path_y),
) -> dict:
    """DELETE /api/v1/raw/{raw_id} — raw 삭제."""
    config = load_config()
    deleted = raw_storage.delete_raw(config.var_dir, raw_id)
    if deleted is None:
        raise ApiError(
            status=404,
            code="E_NOT_FOUND",
            message=f"raw not found: {raw_id}",
        )

    actor = path_y.user_id if path_y else "anonymous"
    audit.append_audit(
        config.var_dir,
        action="raw.delete",
        actor=actor,
        target_type="raw",
        target_id=raw_id,
        details={"source": deleted["source"], "external_id": deleted["external_id"]},
    )

    return envelope.wrap(
        {
            "raw_id": raw_id,
            "deleted": True,
            "source": deleted["source"],
            "external_id": deleted["external_id"],
            "deleted_by": actor,
        }
    )


__all__ = ["router"]
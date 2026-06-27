"""Audit log endpoint (M-v0.0.2-c).

- GET /api/v1/audit?action=...&actor=...&target_type=...&limit=...&offset=... : audit log list

storage: in-memory + var/audit/log.json (storage/audit.py 의 append_audit 가 write)
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ...config import load_config
from ...storage import audit
from ..envelope import EnvelopeContext
from ..middleware import get_envelope


router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("")
async def list_audit(
    action: str | None = Query(None, description="Filter by action (e.g. bundle.create)"),
    actor: str | None = Query(None, description="Filter by actor user_id"),
    target_type: str | None = Query(None, description="Filter by target type (e.g. bundle)"),
    limit: int = Query(50, ge=1, le=200, description="Max items"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    envelope: EnvelopeContext = Depends(get_envelope),
) -> dict:
    """GET /api/v1/audit — audit log list."""
    config = load_config()
    items = audit.list_audit(
        config.var_dir,
        action=action,
        actor=actor,
        target_type=target_type,
        limit=limit,
        offset=offset,
    )
    total = audit.count_audit(config.var_dir)
    return envelope.wrap(
        {"items": items, "total": total, "limit": limit, "offset": offset}
    )


__all__ = ["router"]
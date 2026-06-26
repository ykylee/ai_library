"""Health endpoints (M-v0.0.2-a foundation).

Two routers:
- root_router : GET /health                  (root-level, no /api/v1 prefix)
- protected_router : GET /api/v1/health/protected  (v1 router aggregator 가 include)

두 endpoint 모두 envelope middleware 적용.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ... import __version__
from ..envelope import EnvelopeContext
from ..middleware import get_envelope, get_path_y
from ..path_y import PathYUserContext

# Root-level router (no prefix) — registered at app level in api/__init__.py
root_router = APIRouter(tags=["health"])

# v1-prefixed router — registered in api/v1/__init__.py
protected_router = APIRouter(tags=["health"])


@root_router.get("/health")
async def health(envelope: EnvelopeContext = Depends(get_envelope)) -> dict:
    """Public health check. return `{status, version}`."""
    return envelope.wrap({"status": "ok", "version": __version__})


@protected_router.get("/health/protected")
async def health_protected(
    envelope: EnvelopeContext = Depends(get_envelope),
    path_y: PathYUserContext | None = Depends(get_path_y),
) -> dict:
    """Path Y protected health check.

    caller-provided user context 의 4 field (user_id / org_id / roles / project_ids) 반환.
    Path Y header 없으면 200 + caller_user_id=null (envelope.path_y_validated=false).
    """
    if path_y is None:
        return envelope.wrap(
            {
                "user_id": None,
                "org_id": None,
                "roles": [],
                "project_ids": [],
                "path_y_validated": False,
            }
        )
    return envelope.wrap(
        {
            "user_id": path_y.user_id,
            "org_id": path_y.org_id,
            "roles": list(path_y.roles),
            "project_ids": list(path_y.project_ids),
            "path_y_validated": True,
        }
    )
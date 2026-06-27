"""LLM enrich endpoints (M-v0.0.3-a).

- POST /api/v1/enrich               : 새 enrich job 생성 + 실행
- POST /api/v1/enrich/{job_id}/apply: confirm 모드 job apply
- GET  /api/v1/enrich/jobs          : job list
- GET  /api/v1/enrich/{job_id}      : job detail
- GET  /api/v1/enrich/metrics       : 5 metrics snapshot

3-mode confirm workflow (POST /enrich body 의 `mode` 또는 query `?mode=`):
- dry_run     : result 만, write 안 함
- confirm     : result + applied=false, caller 가 /apply 호출 필요
- auto_apply  : confidence >= 0.9 면 즉시 write

SDK 미설치 시 모든 enrich 호출이 success=False, error_code=E_NOT_IMPLEMENTED 반환.
metrics endpoint 는 SDK 와 독립적 (항상 동작).
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from ...config import load_config
from ...llm import pi_enrich
from ...llm.metrics import get_metrics_store
from ...llm.sdk_client import is_sdk_available
from ...llm.types import EnrichMode, EnrichStatus
from ..envelope import EnvelopeContext
from ..errors import ApiError
from ..middleware import get_envelope, get_path_y
from ..path_y import PathYUserContext


router = APIRouter(prefix="/enrich", tags=["enrich"])


@router.post("")
async def create_enrich(
    body: dict[str, Any],
    envelope: EnvelopeContext = Depends(get_envelope),
    path_y: PathYUserContext | None = Depends(get_path_y),
) -> dict:
    """POST /api/v1/enrich — 새 enrich job 생성 + 실행.

    body:
    - concept_path (required): var/bundles/{bundle}/concepts/{type}/{name}.md
    - mode (optional): "dry_run" | "confirm" | "auto_apply" (default: confirm)
    - prompt_template (optional): custom prompt string
    """
    concept_path = body.get("concept_path")
    if not concept_path or not isinstance(concept_path, str):
        raise ApiError(
            status=400,
            code="E_BAD_REQUEST",
            message="concept_path is required (string)",
        )
    mode = EnrichMode.parse(body.get("mode"))
    prompt_template = body.get("prompt_template")
    actor = path_y.user_id if path_y else "anonymous"

    config = load_config()
    job = await pi_enrich.create_enrich_job(
        concept_path=concept_path,
        mode=mode,
        prompt_template=prompt_template,
        actor=actor,
        var_dir=config.var_dir,
    )

    data = job.to_dict()
    data["applied"] = job.applied_at is not None
    data["sdk_available"] = is_sdk_available()
    return envelope.wrap(data)


@router.post("/{job_id}/apply")
async def apply_enrich(
    job_id: str,
    envelope: EnvelopeContext = Depends(get_envelope),
    path_y: PathYUserContext | None = Depends(get_path_y),
) -> dict:
    """POST /api/v1/enrich/{job_id}/apply — confirm 모드 job apply."""
    actor = path_y.user_id if path_y else "anonymous"
    config = load_config()
    try:
        job = pi_enrich.apply_job(job_id, actor=actor, var_dir=config.var_dir)
    except KeyError:
        raise ApiError(status=404, code="E_NOT_FOUND", message=f"job not found: {job_id}")
    except ValueError as e:
        raise ApiError(status=409, code="E_CONFLICT", message=str(e))
    except RuntimeError as e:
        raise ApiError(status=500, code="E_INTERNAL", message=str(e))

    data = job.to_dict()
    data["applied"] = True
    return envelope.wrap(data)


@router.get("/jobs")
async def list_enrich_jobs(
    status: str | None = Query(None, description="Filter by status"),
    mode: str | None = Query(None, description="Filter by mode"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    envelope: EnvelopeContext = Depends(get_envelope),
) -> dict:
    """GET /api/v1/enrich/jobs — job list."""
    status_enum: EnrichStatus | None = None
    if status is not None:
        try:
            status_enum = EnrichStatus(status)
        except ValueError:
            raise ApiError(
                status=400,
                code="E_BAD_REQUEST",
                message=f"invalid status: {status}",
            )
    mode_enum: EnrichMode | None = None
    if mode is not None:
        try:
            mode_enum = EnrichMode(mode)
        except ValueError:
            raise ApiError(
                status=400,
                code="E_BAD_REQUEST",
                message=f"invalid mode: {mode}",
            )

    jobs = pi_enrich.list_jobs(status=status_enum, mode=mode_enum, limit=limit, offset=offset)
    total = pi_enrich.count_jobs()
    return envelope.wrap(
        {
            "items": [j.to_dict() for j in jobs],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    )


@router.get("/metrics")
async def get_enrich_metrics(
    envelope: EnvelopeContext = Depends(get_envelope),
) -> dict:
    """GET /api/v1/enrich/metrics — 5 metrics snapshot."""
    snapshot = get_metrics_store().snapshot()
    data = snapshot.to_dict()
    data["sdk_available"] = is_sdk_available()
    return envelope.wrap(data)


@router.get("/{job_id}")
async def get_enrich_job(
    job_id: str,
    envelope: EnvelopeContext = Depends(get_envelope),
) -> dict:
    """GET /api/v1/enrich/{job_id} — job detail."""
    job = pi_enrich.get_job(job_id)
    if job is None:
        raise ApiError(status=404, code="E_NOT_FOUND", message=f"job not found: {job_id}")
    data = job.to_dict()
    data["applied"] = job.applied_at is not None
    return envelope.wrap(data)


__all__ = ["router"]
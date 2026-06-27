"""Monitoring alerts endpoint (M-v0.0.2-c).

- GET /api/v1/monitoring/alerts?severity=critical|warning|info : 3-tier alert stub

3-tier alert model:
- critical : 즉각 대응 필요 (source plugin auth_failure > N, bundle conflict, ...)
- warning  : 주의 (queue depth > threshold, latency p95 > SLO, ...)
- info     : 정보 (source 새 release, 정기 maintenance, ...)

M-v0.0.2-c scope = in-memory mock list (registry / bundles / raw 기반 simple heuristic).
M-v0.0.5+ 에서 real metric collector 통합.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Query

from ...config import load_config
from ...sources.registry import all_sources
from ..envelope import EnvelopeContext
from ..middleware import get_envelope


router = APIRouter(prefix="/monitoring", tags=["monitoring"])


VALID_SEVERITIES = {"critical", "warning", "info"}


def _build_alerts(var_dir) -> list[dict[str, Any]]:
    """Simple heuristic 으로 alert list 생성.

    rules (M-v0.0.2-c stub):
    - source.state == "error" → warning
    - source.auth_failures >= 1 → critical
    - var/bundles/ 비어있으면 info ("no bundles yet")
    """
    now = datetime.now(timezone.utc).isoformat()
    alerts: list[dict[str, Any]] = []

    for src in all_sources():
        if src.state == "error":
            alerts.append(
                {
                    "alert_id": f"alert_src_err_{src.name}",
                    "severity": "warning",
                    "category": "source",
                    "target": src.name,
                    "message": f"source '{src.name}' is in error state",
                    "details": src.last_error or {},
                    "raised_at": src.last_sync or now,
                }
            )
        if src.auth_failures >= 1:
            alerts.append(
                {
                    "alert_id": f"alert_src_auth_{src.name}",
                    "severity": "critical",
                    "category": "source",
                    "target": src.name,
                    "message": f"source '{src.name}' has {src.auth_failures} auth failures",
                    "details": {"auth_failures": src.auth_failures},
                    "raised_at": now,
                }
            )

    # bundle empty
    bundles_dir = var_dir / "bundles"
    if not bundles_dir.exists() or not any(bundles_dir.iterdir()):
        alerts.append(
            {
                "alert_id": "alert_no_bundles",
                "severity": "info",
                "category": "bundle",
                "target": "*",
                "message": "no bundles configured yet",
                "details": {},
                "raised_at": now,
            }
        )

    return alerts


@router.get("/alerts")
async def list_alerts(
    severity: str | None = Query(None, description="Filter by severity (critical|warning|info)"),
    envelope: EnvelopeContext = Depends(get_envelope),
) -> dict:
    """GET /api/v1/monitoring/alerts — 3-tier alert list."""
    if severity is not None and severity not in VALID_SEVERITIES:
        from ..errors import ApiError

        raise ApiError(
            status=400,
            code="E_BAD_REQUEST",
            message=f"invalid severity: {severity} (valid: {sorted(VALID_SEVERITIES)})",
        )

    config = load_config()
    alerts = _build_alerts(config.var_dir)
    if severity is not None:
        alerts = [a for a in alerts if a["severity"] == severity]

    # severity 순 정렬 (critical > warning > info)
    sev_order = {"critical": 0, "warning": 1, "info": 2}
    alerts.sort(key=lambda a: (sev_order.get(a["severity"], 99), a["alert_id"]))

    return envelope.wrap(
        {
            "alerts": alerts,
            "total": len(alerts),
            "by_severity": {
                s: sum(1 for a in alerts if a["severity"] == s)
                for s in ("critical", "warning", "info")
            },
        }
    )


__all__ = ["router", "VALID_SEVERITIES"]
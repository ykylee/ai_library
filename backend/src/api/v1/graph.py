"""Cross-link graph endpoint (M-v0.0.2-c).

- GET  /api/v1/graph?bundle=... : cross-link graph read (var/bundles/{bundle}/cross-link/graph.json)
- POST /api/v1/graph/reindex?bundle=...&dry_run=... : rebuild cross-link from bundles

M-v0.0.2-c scope = stub. 실제 cross-link 계산 (concept 간 link 추출) 은 M-v0.0.5+.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, Query

from ...config import load_config
from ...storage import audit
from ..envelope import EnvelopeContext
from ..errors import ApiError
from ..middleware import get_envelope, get_path_y
from ..path_y import PathYUserContext
from ...storage import read_json, write_json


router = APIRouter(prefix="/graph", tags=["graph"])


def _bundle_dir(bundle: str, var_dir: Path) -> Path:
    """Bundle 디렉터리 경로 (bundles.py 와 동일, circular import 회피 위해 inline)."""
    return var_dir / "bundles" / bundle


def _graph_path(var_dir: Path, bundle: str) -> Path:
    """var/bundles/{bundle}/cross-link/graph.json 경로."""
    return _bundle_dir(bundle, var_dir) / "cross-link" / "graph.json"


def _read_graph(var_dir: Path, bundle: str) -> dict[str, Any] | None:
    return read_json(_graph_path(var_dir, bundle))


def _count_concepts(bundle_dir: Path) -> int:
    concepts_dir = bundle_dir / "concepts"
    if not concepts_dir.exists():
        return 0
    return sum(1 for f in concepts_dir.glob("*.md"))


@router.get("")
async def get_graph(
    bundle: str | None = Query(None, description="Specific bundle (omit 시 all bundles)"),
    envelope: EnvelopeContext = Depends(get_envelope),
) -> dict:
    """GET /api/v1/graph?bundle=... — cross-link graph."""
    config = load_config()
    bundles_dir = config.var_dir / "bundles"
    if not bundles_dir.exists():
        return envelope.wrap({"graphs": [], "total": 0})

    graphs: list[dict[str, Any]] = []
    for bundle_dir in sorted(bundles_dir.iterdir()):
        if not bundle_dir.is_dir():
            continue
        if bundle is not None and bundle_dir.name != bundle:
            continue
        graph = _read_graph(config.var_dir, bundle_dir.name)
        if graph is not None:
            graphs.append({"bundle": bundle_dir.name, **graph})

    return envelope.wrap({"graphs": graphs, "total": len(graphs)})


@router.post("/reindex")
async def reindex_graph(
    bundle: str = Query(..., description="Bundle name to reindex"),
    dry_run: bool = Query(False, description="Dry-run mode (실제 write 안 함)"),
    envelope: EnvelopeContext = Depends(get_envelope),
    path_y: PathYUserContext | None = Depends(get_path_y),
) -> dict:
    """POST /api/v1/graph/reindex?bundle=...&dry_run=... — rebuild cross-link graph."""
    config = load_config()
    bundle_dir = _bundle_dir(bundle, config.var_dir)
    if not bundle_dir.exists():
        raise ApiError(
            status=404,
            code="E_NOT_FOUND",
            message=f"bundle not found: {bundle}",
        )

    started = datetime.now(timezone.utc)
    concept_count = _count_concepts(bundle_dir)
    # M-v0.0.2-c stub: link_count estimate (concept_count * 2)
    link_count = concept_count * 2

    if not dry_run:
        cross_link_dir = bundle_dir / "cross-link"
        cross_link_dir.mkdir(exist_ok=True)
        graph_data = {
            "bundle": bundle,
            "concept_count": concept_count,
            "link_count": link_count,
            "reindexed_at": started.isoformat(),
            "reindexed_by": path_y.user_id if path_y else "anonymous",
        }
        write_json(cross_link_dir / "graph.json", graph_data, atomic=True)

        # audit 기록
        audit.append_audit(
            config.var_dir,
            action="graph.reindex",
            actor=path_y.user_id if path_y else "anonymous",
            target_type="bundle",
            target_id=bundle,
            details={"concept_count": concept_count, "link_count": link_count},
        )

    finished = datetime.now(timezone.utc)
    duration_ms = int((finished - started).total_seconds() * 1000)

    return envelope.wrap(
        {
            "bundle": bundle,
            "concept_count": concept_count,
            "link_count": link_count,
            "dry_run": dry_run,
            "duration_ms": duration_ms,
            "reindexed_at": finished.isoformat(),
        }
    )


__all__ = ["router"]
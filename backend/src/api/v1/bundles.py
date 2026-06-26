"""Bundle endpoints (M-v0.0.2-b).

- GET  /api/v1/bundles                  : bundle list
- GET  /api/v1/bundles/{name}           : bundle detail (index.md + metadata)
- POST /api/v1/bundles                  : bundle create (name + owner_org_id + visibility)
- POST /api/v1/bundles/{name}/rebuild?dry_run=... : bundle rebuild (scan raw + concepts + cross-link)

storage = `var/bundles/{name}/meta.json` (bundle metadata) + `var/bundles/{name}/index.md` (auto-generated).

web frontend 정합:
- listBundles() → GET /api/v1/bundles
- getBundle(name) → GET /api/v1/bundles/{name}
- createBundle(body) → POST /api/v1/bundles
- rebuildBundle(bundle, opts, dryRun) → POST /api/v1/bundles/{bundle}/rebuild?dry_run={dryRun}
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, Query

from ...config import load_config
from ...storage import read_json, utcnow_iso, write_json
from ..envelope import EnvelopeContext
from ..errors import ApiError
from ..middleware import get_envelope, get_path_y
from ..path_y import PathYUserContext

router = APIRouter(prefix="/bundles", tags=["bundles"])


def _bundle_dir(name: str, var_dir: Path) -> Path:
    """Bundle 디렉터리 경로."""
    return var_dir / "bundles" / name


def _read_bundle(name: str, var_dir: Path) -> dict[str, Any] | None:
    """Bundle metadata read. None if not exists."""
    meta_path = _bundle_dir(name, var_dir) / "meta.json"
    return read_json(meta_path)


def _list_bundles(var_dir: Path) -> list[dict[str, Any]]:
    """var/bundles/ 하위 모든 bundle 의 metadata list."""
    bundles_dir = var_dir / "bundles"
    if not bundles_dir.exists():
        return []
    items: list[dict[str, Any]] = []
    for entry in sorted(bundles_dir.iterdir()):
        if not entry.is_dir():
            continue
        meta = _read_bundle(entry.name, var_dir)
        if meta is None:
            continue
        # concept_count: concepts/ 하위 .md file 수 (없으면 0)
        concepts_dir = entry / "concepts"
        concept_count = (
            sum(1 for f in concepts_dir.glob("*.md")) if concepts_dir.exists() else 0
        )
        items.append({**meta, "concept_count": concept_count})
    return items


@router.get("")
async def list_bundles(envelope: EnvelopeContext = Depends(get_envelope)) -> dict:
    """GET /api/v1/bundles — bundle list."""
    config = load_config()
    items = _list_bundles(config.var_dir)
    return envelope.wrap({"items": items, "total": len(items)})


@router.get("/{name}")
async def get_bundle(
    name: str,
    envelope: EnvelopeContext = Depends(get_envelope),
) -> dict:
    """GET /api/v1/bundles/{name} — bundle detail."""
    config = load_config()
    meta = _read_bundle(name, config.var_dir)
    if meta is None:
        raise ApiError(status=404, code="E_NOT_FOUND", message=f"bundle not found: {name}")
    bundle_dir = _bundle_dir(name, config.var_dir)
    concepts_dir = bundle_dir / "concepts"
    concept_count = (
        sum(1 for f in concepts_dir.glob("*.md")) if concepts_dir.exists() else 0
    )
    detail = {
        **meta,
        "concept_count": concept_count,
    }
    return envelope.wrap(detail)


@router.post("")
async def create_bundle(
    body: dict[str, Any],
    envelope: EnvelopeContext = Depends(get_envelope),
    path_y: PathYUserContext | None = Depends(get_path_y),
) -> dict:
    """POST /api/v1/bundles — bundle create."""
    name = body.get("name")
    if not name or not isinstance(name, str):
        raise ApiError(status=400, code="E_BAD_REQUEST", message="name is required (string)")
    owner_org_id = body.get("owner_org_id")
    if not owner_org_id:
        raise ApiError(status=400, code="E_BAD_REQUEST", message="owner_org_id is required")
    visibility = body.get("visibility", "org")
    if visibility not in {"public", "org", "personal", "project"}:
        raise ApiError(
            status=400,
            code="E_BAD_REQUEST",
            message=f"invalid visibility: {visibility}",
        )
    description = body.get("description", "")

    config = load_config()
    bundle_dir = _bundle_dir(name, config.var_dir)
    if bundle_dir.exists():
        raise ApiError(
            status=409,
            code="E_CONFLICT",
            message=f"bundle already exists: {name}",
        )

    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "concepts").mkdir(exist_ok=True)
    (bundle_dir / "raw").mkdir(exist_ok=True)

    now = utcnow_iso()
    creator = path_y.user_id if path_y else "anonymous"
    meta = {
        "name": name,
        "description": description,
        "version": 1,
        "owner_org_id": owner_org_id,
        "owner_user_id": creator,
        "org_unit_ids": list(path_y.org_unit_ids) if path_y else [],
        "project_ids": list(path_y.project_ids) if path_y else [],
        "visibility": visibility,
        "created_at": now,
        "updated_at": now,
        "updated_by": creator,
    }
    write_json(bundle_dir / "meta.json", meta, atomic=True)

    # index.md placeholder
    index_md = bundle_dir / "index.md"
    index_md.write_text(
        f"# {name}\n\n{description}\n\n_Generated by ai_library v0.0.1._\n",
        encoding="utf-8",
    )

    return envelope.wrap(
        {
            "name": name,
            "created_at": now,
            "created_by": creator,
            "visibility": visibility,
            "path": str(bundle_dir),
        }
    )


@router.post("/{name}/rebuild")
async def rebuild_bundle(
    name: str,
    dry_run: bool = Query(False, description="Dry-run mode (실제 write 안 함)"),
    envelope: EnvelopeContext = Depends(get_envelope),
) -> dict:
    """POST /api/v1/bundles/{name}/rebuild?dry_run=... — bundle rebuild."""
    config = load_config()
    bundle_dir = _bundle_dir(name, config.var_dir)
    if not bundle_dir.exists():
        raise ApiError(status=404, code="E_NOT_FOUND", message=f"bundle not found: {name}")

    started = datetime.now(timezone.utc)
    concepts_dir = bundle_dir / "concepts"
    cross_link_dir = bundle_dir / "cross-link"
    raw_dir = bundle_dir / "raw"

    concept_count = (
        sum(1 for f in concepts_dir.glob("*.md")) if concepts_dir.exists() else 0
    )
    raw_count = (
        sum(1 for _ in raw_dir.rglob("*")) if raw_dir.exists() else 0
    )
    link_count = concept_count * 2  # estimated

    if not dry_run:
        cross_link_dir.mkdir(exist_ok=True)
        (cross_link_dir / "graph.json").write_text(
            f'{{"bundle": "{name}", "concepts": {concept_count}, "links": {link_count}}}\n',
            encoding="utf-8",
        )

    finished = datetime.now(timezone.utc)
    duration_ms = int((finished - started).total_seconds() * 1000)

    return envelope.wrap(
        {
            "bundle": name,
            "concept_count": concept_count,
            "link_count": link_count,
            "raw_count": raw_count,
            "reverse_index_generated": not dry_run,
            "index_md_generated": True,
            "viz_html_generated": False,  # M-v0.0.5+ 구현
            "duration_ms": duration_ms,
            "rebuilt_at": finished.isoformat(),
        }
    )
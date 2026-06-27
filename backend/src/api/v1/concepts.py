"""Concept search + detail endpoints (M-v0.0.2-c).

- GET /api/v1/search?q=...&type=...&bundle=... : concept 검색 (in-memory inverted index)
- GET /api/v1/concepts/{type}/{name}?bundle=... : concept 상세 (bundle filter optional)

concept storage:
- var/bundles/{bundle}/concepts/{type}/{name}.md (markdown file, OKF 정합)
- index.md auto-generated per bundle (M-v0.0.2-b 의 rebuild 가 생성)

in-memory inverted index:
- module load 시 var/bundles/*/concepts/ scan → {term: [(bundle, type, name), ...]}
- query 시 simple substring + token match (M-v0.0.5+ 에서 real FTS 로 교체 가능)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, Query

from ...config import load_config
from ..envelope import EnvelopeContext
from ..errors import ApiError
from ..middleware import get_envelope


router = APIRouter(tags=["concepts"])

# 8종 OKF concept type enum (backend/okf/SPEC.md §3.6 정합)
VALID_CONCEPT_TYPES = {
    "adr",
    "rfc",
    "runbook",
    "postmortem",
    "concept",
    "howto",
    "policy",
    "glossary",
}


def _concept_path(var_dir: Path, bundle: str, ctype: str, name: str) -> Path:
    """var/bundles/{bundle}/concepts/{type}/{name}.md 경로."""
    return var_dir / "bundles" / bundle / "concepts" / ctype / f"{name}.md"


def _read_concept(var_dir: Path, bundle: str, ctype: str, name: str) -> dict[str, Any] | None:
    """Concept markdown + metadata read. None if not exists."""
    path = _concept_path(var_dir, bundle, ctype, name)
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    # extract title from first `# ` heading
    title = name
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    # simple word count + link count
    word_count = len(text.split())
    link_count = text.count("](http") + text.count("](/")
    return {
        "bundle": bundle,
        "type": ctype,
        "name": name,
        "title": title,
        "path": str(path),
        "word_count": word_count,
        "link_count": link_count,
        "body": text,
    }


def _build_inverted_index(var_dir: Path) -> dict[str, list[dict[str, str]]]:
    """var/bundles/*/concepts/ 전체 scan → inverted index.

    Returns: {term_lower: [{"bundle", "type", "name"}, ...]}
    """
    bundles_dir = var_dir / "bundles"
    if not bundles_dir.exists():
        return {}
    index: dict[str, list[dict[str, str]]] = {}
    for bundle_dir in sorted(bundles_dir.iterdir()):
        if not bundle_dir.is_dir():
            continue
        concepts_dir = bundle_dir / "concepts"
        if not concepts_dir.exists():
            continue
        for type_dir in sorted(concepts_dir.iterdir()):
            if not type_dir.is_dir():
                continue
            ctype = type_dir.name
            for md_file in sorted(type_dir.glob("*.md")):
                name = md_file.stem
                # naive tokenization: name + title from heading
                try:
                    text = md_file.read_text(encoding="utf-8")
                except OSError:
                    continue
                tokens = {name.lower()}
                for line in text.splitlines()[:10]:  # 제목 영역만 (M-v0.0.2-c scope)
                    if line.startswith("# "):
                        tokens.update(t.lower() for t in line[2:].split())
                for tok in tokens:
                    if not tok:
                        continue
                    index.setdefault(tok, []).append(
                        {"bundle": bundle_dir.name, "type": ctype, "name": name}
                    )
    return index


@router.get("/search")
async def search_concepts(
    q: str = Query(..., description="Search query (token substring match)"),
    type: str | None = Query(None, description="Filter by concept type"),
    bundle: str | None = Query(None, description="Filter by bundle"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    envelope: EnvelopeContext = Depends(get_envelope),
) -> dict:
    """GET /api/v1/search?q=... — concept 검색."""
    config = load_config()
    index = _build_inverted_index(config.var_dir)

    q_tokens = [t.lower() for t in q.split() if t]
    if not q_tokens:
        return envelope.wrap({"results": [], "total": 0, "query": q})

    # score: token hit count per concept
    candidates: dict[tuple[str, str, str], int] = {}
    for tok in q_tokens:
        # prefix/substring match
        for index_tok, refs in index.items():
            if tok in index_tok:
                for ref in refs:
                    key = (ref["bundle"], ref["type"], ref["name"])
                    candidates[key] = candidates.get(key, 0) + 1

    results: list[dict[str, Any]] = []
    for (b, t, n), score in sorted(candidates.items(), key=lambda x: -x[1])[:limit]:
        if type is not None and t != type:
            continue
        if bundle is not None and b != bundle:
            continue
        results.append(
            {
                "bundle": b,
                "type": t,
                "name": n,
                "score": score,
                "title": n,
            }
        )

    return envelope.wrap({"results": results, "total": len(results), "query": q})


@router.get("/concepts/{type}/{name}")
async def get_concept(
    type: str,
    name: str,
    bundle: str | None = Query(None, description="Specific bundle (omit 시 모든 bundle search)"),
    envelope: EnvelopeContext = Depends(get_envelope),
) -> dict:
    """GET /api/v1/concepts/{type}/{name}?bundle=... — concept 상세."""
    if type not in VALID_CONCEPT_TYPES:
        raise ApiError(
            status=400,
            code="E_BAD_REQUEST",
            message=f"invalid concept type: {type} (valid: {sorted(VALID_CONCEPT_TYPES)})",
        )

    config = load_config()

    if bundle is not None:
        concept = _read_concept(config.var_dir, bundle, type, name)
        if concept is None:
            raise ApiError(
                status=404,
                code="E_NOT_FOUND",
                message=f"concept not found: {bundle}/{type}/{name}",
            )
        return envelope.wrap(concept)

    # bundle 미지정 시 모든 bundle 에서 검색
    bundles_dir = config.var_dir / "bundles"
    found: list[dict[str, Any]] = []
    if bundles_dir.exists():
        for bundle_dir in sorted(bundles_dir.iterdir()):
            if not bundle_dir.is_dir():
                continue
            concept = _read_concept(config.var_dir, bundle_dir.name, type, name)
            if concept is not None:
                found.append(concept)
    if not found:
        raise ApiError(
            status=404,
            code="E_NOT_FOUND",
            message=f"concept not found: type={type} name={name} (any bundle)",
        )
    return envelope.wrap({"results": found, "total": len(found)})


__all__ = ["router", "VALID_CONCEPT_TYPES"]
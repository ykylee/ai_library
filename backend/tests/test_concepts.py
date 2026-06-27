"""Concept endpoint tests (M-v0.0.2-c).

GET /api/v1/search + GET /api/v1/concepts/{type}/{name}
"""
from __future__ import annotations

import pytest
import uuid
from fastapi.testclient import TestClient

from src.main import create_app


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


@pytest.fixture
def bundle_name() -> str:
    return f"smoke-bundle-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def concept_bundle(client: TestClient, bundle_name: str):
    """Bundle + 2 concept (adr/timeout-policy, runbook/restart) 생성."""
    res = client.post(
        "/api/v1/bundles",
        json={
            "name": bundle_name,
            "owner_org_id": "ou_test",
            "visibility": "org",
        },
    )
    assert res.status_code == 200

    # 직접 concept markdown file 작성 (M-v0.0.2-c: endpoint 는 검색/조회만, 생성은 bundles 에서)
    import json
    from pathlib import Path
    from src.config import load_config
    config = load_config()
    bundle_dir = config.var_dir / "bundles" / bundle_name / "concepts"
    for ctype, name, title in [
        ("adr", "timeout-policy", "Timeout Policy Decision"),
        ("runbook", "restart", "Service Restart Runbook"),
    ]:
        cdir = bundle_dir / ctype
        cdir.mkdir(parents=True, exist_ok=True)
        (cdir / f"{name}.md").write_text(
            f"# {title}\n\nDetailed body for {name}.\n",
            encoding="utf-8",
        )
    return bundle_name


class TestSearchConcepts:
    """GET /api/v1/search — concept 검색."""

    def test_search_empty_query_returns_zero(self, client: TestClient) -> None:
        # multi-token query 필수 (현재 구현에서 q_tokens 비면 total=0)
        res = client.get("/api/v1/search?q=__nonexistent_term_xyz__")
        assert res.status_code == 200
        assert res.json()["data"]["total"] == 0

    def test_search_finds_concept_by_name_token(self, client: TestClient, concept_bundle) -> None:
        res = client.get("/api/v1/search?q=timeout")
        assert res.status_code == 200
        body = res.json()
        assert body["data"]["total"] >= 1
        names = [r["name"] for r in body["data"]["results"]]
        assert "timeout-policy" in names

    def test_search_filters_by_bundle(self, client: TestClient, concept_bundle) -> None:
        res = client.get(f"/api/v1/search?q=restart&bundle={concept_bundle}")
        assert res.status_code == 200
        body = res.json()
        for r in body["data"]["results"]:
            assert r["bundle"] == concept_bundle

    def test_search_filters_by_type(self, client: TestClient, concept_bundle) -> None:
        res = client.get(f"/api/v1/search?q=restart&type=runbook")
        assert res.status_code == 200
        for r in res.json()["data"]["results"]:
            assert r["type"] == "runbook"


class TestGetConcept:
    """GET /api/v1/concepts/{type}/{name} — concept 상세."""

    def test_get_concept_with_bundle(self, client: TestClient, concept_bundle) -> None:
        res = client.get(f"/api/v1/concepts/adr/timeout-policy?bundle={concept_bundle}")
        assert res.status_code == 200
        body = res.json()
        assert body["data"]["bundle"] == concept_bundle
        assert body["data"]["type"] == "adr"
        assert body["data"]["name"] == "timeout-policy"

    def test_get_concept_invalid_type_returns_400(self, client: TestClient) -> None:
        res = client.get("/api/v1/concepts/invalid_type/foo")
        assert res.status_code == 400
        assert res.json()["detail"]["code"] == "E_BAD_REQUEST"

    def test_get_concept_nonexistent_returns_404(self, client: TestClient, concept_bundle) -> None:
        res = client.get(f"/api/v1/concepts/adr/nonexistent?bundle={concept_bundle}")
        assert res.status_code == 404

    def test_get_concept_without_bundle_searches_all(
        self, client: TestClient, concept_bundle
    ) -> None:
        # bundle 없이 검색 시 모든 bundle 에서 찾음
        res = client.get("/api/v1/concepts/runbook/restart")
        assert res.status_code == 200
        body = res.json()
        assert body["data"]["total"] >= 1
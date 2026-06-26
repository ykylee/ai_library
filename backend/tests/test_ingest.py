"""Ingest endpoint tests (M-v0.0.2-b)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.main import create_app


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


class TestIngestStatuses:
    """GET /api/v1/ingest/statuses — 5종 source 의 현재 상태 list."""

    def test_returns_5_sources(self, client: TestClient) -> None:
        res = client.get("/api/v1/ingest/statuses")
        assert res.status_code == 200
        body = res.json()
        assert "data" in body
        assert body["data"]["total"] == 5
        assert len(body["data"]["sources"]) == 5

    def test_all_5_names_present(self, client: TestClient) -> None:
        res = client.get("/api/v1/ingest/statuses")
        sources = [s["source"] for s in res.json()["data"]["sources"]]
        assert "mock" in sources
        assert "gitea_repo_pull" in sources
        assert "gitea_issue" in sources
        assert "gitea_wiki" in sources
        assert "gitea_action" in sources

    def test_envelope_wrapped(self, client: TestClient) -> None:
        res = client.get("/api/v1/ingest/statuses")
        assert res.json()["envelope"]["api_version"] == "v1"


class TestIngestSync:
    """POST /api/v1/ingest/{source}/sync — sync trigger."""

    def test_mock_sync_dry_run(self, client: TestClient) -> None:
        res = client.post("/api/v1/ingest/mock/sync?dry_run=true")
        assert res.status_code == 200
        body = res.json()
        assert body["data"]["synced"] == 1
        assert body["data"]["failed"] == 0
        assert body["data"]["errors"] == []

    def test_gitea_source_returns_not_implemented(self, client: TestClient) -> None:
        res = client.post("/api/v1/ingest/gitea_repo_pull/sync")
        assert res.status_code == 200
        body = res.json()
        assert body["data"]["synced"] == 0
        assert len(body["data"]["errors"]) == 1
        assert body["data"]["errors"][0]["code"] == "E_NOT_IMPLEMENTED"

    def test_unknown_source_returns_404(self, client: TestClient) -> None:
        res = client.post("/api/v1/ingest/unknown_source/sync")
        assert res.status_code == 404
        assert res.json()["detail"]["code"] == "E_NOT_FOUND"


class TestIngestPull:
    """POST /api/v1/ingest/{source}/pull — pull new data."""

    def test_mock_pull_returns_raw_ids(self, client: TestClient) -> None:
        res = client.post("/api/v1/ingest/mock/pull")
        assert res.status_code == 200
        body = res.json()
        assert body["data"]["pulled"] == 1
        assert len(body["data"]["raw_ids"]) == 1

    def test_gitea_pull_returns_not_implemented(self, client: TestClient) -> None:
        res = client.post("/api/v1/ingest/gitea_issue/pull")
        assert res.status_code == 200
        body = res.json()
        assert body["data"]["pulled"] == 0
        assert body["data"]["errors"][0]["code"] == "E_NOT_IMPLEMENTED"
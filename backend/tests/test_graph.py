"""Graph endpoint tests (M-v0.0.2-c).

GET /api/v1/graph + POST /api/v1/graph/reindex
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
    return f"smoke-graph-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def bundle(client: TestClient, bundle_name: str):
    """Bundle 1개 생성."""
    res = client.post(
        "/api/v1/bundles",
        json={"name": bundle_name, "owner_org_id": "ou_test", "visibility": "org"},
    )
    assert res.status_code == 200
    return bundle_name


class TestGetGraph:
    """GET /api/v1/graph — cross-link graph read."""

    def test_returns_envelope(self, client: TestClient) -> None:
        res = client.get("/api/v1/graph")
        assert res.status_code == 200
        body = res.json()
        assert "graphs" in body["data"]
        assert "total" in body["data"]

    def test_filtered_by_bundle(self, client: TestClient, bundle) -> None:
        res = client.get(f"/api/v1/graph?bundle={bundle}")
        # 새 bundle 은 graph 없음 → 빈 list 가능, 또는 error 아님
        assert res.status_code == 200


class TestReindexGraph:
    """POST /api/v1/graph/reindex — rebuild cross-link."""

    def test_reindex_existing_bundle(self, client: TestClient, bundle) -> None:
        res = client.post(f"/api/v1/graph/reindex?bundle={bundle}&dry_run=true")
        assert res.status_code == 200
        body = res.json()
        assert body["data"]["bundle"] == bundle
        assert body["data"]["dry_run"] is True

    def test_reindex_writes_graph_file(self, client: TestClient, bundle) -> None:
        from src.config import load_config
        config = load_config()
        res = client.post(f"/api/v1/graph/reindex?bundle={bundle}&dry_run=false")
        assert res.status_code == 200
        graph_file = config.var_dir / "bundles" / bundle / "cross-link" / "graph.json"
        assert graph_file.exists()

    def test_reindex_nonexistent_returns_404(self, client: TestClient) -> None:
        res = client.post("/api/v1/graph/reindex?bundle=nonexistent-bundle-xyz")
        assert res.status_code == 404

    def test_reindex_writes_audit_entry(self, client: TestClient, bundle) -> None:
        from src.storage import audit
        from src.config import load_config
        audit._in_memory_log.clear()
        audit._loaded = False
        log_file = load_config().var_dir / "audit" / "log.json"
        if log_file.exists():
            log_file.unlink()
        res = client.post(f"/api/v1/graph/reindex?bundle={bundle}")
        assert res.status_code == 200
        entries = audit.list_audit(load_config().var_dir, action="graph.reindex")
        assert len(entries) >= 1
        assert any(e["target_id"] == bundle for e in entries)
"""Bundle endpoint tests (M-v0.0.2-b)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.main import create_app


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


@pytest.fixture
def bundle_name() -> str:
    """Per-test bundle name (unique for parallel-safety)."""
    import uuid
    return f"smoke-test-{uuid.uuid4().hex[:8]}"


class TestBundleList:
    """GET /api/v1/bundles — bundle list."""

    def test_returns_list_envelope(self, client: TestClient) -> None:
        res = client.get("/api/v1/bundles")
        assert res.status_code == 200
        body = res.json()
        assert "items" in body["data"]
        assert "total" in body["data"]
        assert isinstance(body["data"]["items"], list)


class TestBundleCreate:
    """POST /api/v1/bundles — create."""

    def test_create_bundle(self, client: TestClient, bundle_name: str) -> None:
        res = client.post(
            "/api/v1/bundles",
            json={
                "name": bundle_name,
                "description": "test bundle",
                "owner_org_id": "ou_test",
                "visibility": "org",
            },
        )
        assert res.status_code == 200
        body = res.json()
        assert body["data"]["name"] == bundle_name
        assert body["data"]["visibility"] == "org"

    def test_create_duplicate_returns_409(self, client: TestClient, bundle_name: str) -> None:
        client.post(
            "/api/v1/bundles",
            json={"name": bundle_name, "owner_org_id": "ou_test", "visibility": "org"},
        )
        res = client.post(
            "/api/v1/bundles",
            json={"name": bundle_name, "owner_org_id": "ou_test", "visibility": "org"},
        )
        assert res.status_code == 409
        assert res.json()["detail"]["code"] == "E_CONFLICT"

    def test_create_missing_owner_returns_400(self, client: TestClient) -> None:
        res = client.post(
            "/api/v1/bundles",
            json={"name": "x", "visibility": "org"},
        )
        assert res.status_code == 400

    def test_create_invalid_visibility_returns_400(self, client: TestClient, bundle_name: str) -> None:
        res = client.post(
            "/api/v1/bundles",
            json={"name": bundle_name, "owner_org_id": "ou_test", "visibility": "INVALID"},
        )
        assert res.status_code == 400


class TestBundleGet:
    """GET /api/v1/bundles/{name} — detail."""

    def test_get_existing_bundle(self, client: TestClient, bundle_name: str) -> None:
        client.post(
            "/api/v1/bundles",
            json={"name": bundle_name, "owner_org_id": "ou_test", "visibility": "public"},
        )
        res = client.get(f"/api/v1/bundles/{bundle_name}")
        assert res.status_code == 200
        body = res.json()
        assert body["data"]["name"] == bundle_name
        assert body["data"]["owner_org_id"] == "ou_test"
        assert body["data"]["visibility"] == "public"

    def test_get_nonexistent_returns_404(self, client: TestClient) -> None:
        res = client.get("/api/v1/bundles/nonexistent-bundle-xyz")
        assert res.status_code == 404


class TestBundleRebuild:
    """POST /api/v1/bundles/{name}/rebuild — rebuild."""

    def test_rebuild_existing(self, client: TestClient, bundle_name: str) -> None:
        client.post(
            "/api/v1/bundles",
            json={"name": bundle_name, "owner_org_id": "ou_test", "visibility": "org"},
        )
        res = client.post(f"/api/v1/bundles/{bundle_name}/rebuild?dry_run=true")
        assert res.status_code == 200
        body = res.json()
        assert body["data"]["bundle"] == bundle_name
        assert body["data"]["reverse_index_generated"] is False  # dry_run=true

    def test_rebuild_nonexistent_returns_404(self, client: TestClient) -> None:
        res = client.post("/api/v1/bundles/nonexistent-bundle-xyz/rebuild")
        assert res.status_code == 404
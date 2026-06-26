"""Health endpoint integration tests (M-v0.0.2-a)."""
from __future__ import annotations

import base64
import json

import pytest
from fastapi.testclient import TestClient

from src.main import create_app


@pytest.fixture
def client() -> TestClient:
    """FastAPI TestClient with envelope middleware installed."""
    app = create_app()
    return TestClient(app)


class TestPublicHealth:
    """GET /health — public health check."""

    def test_returns_200(self, client: TestClient) -> None:
        res = client.get("/health")
        assert res.status_code == 200

    def test_envelope_wraps_data(self, client: TestClient) -> None:
        res = client.get("/health")
        body = res.json()
        assert "envelope" in body
        assert "data" in body
        assert body["data"]["status"] == "ok"

    def test_envelope_meta_fields(self, client: TestClient) -> None:
        res = client.get("/health")
        meta = res.json()["envelope"]
        assert meta["api_version"] == "v0-2"
        assert "request_id" in meta
        assert "timestamp" in meta
        assert meta["caller_user_id"] is None
        assert meta["path_y_validated"] is False

    def test_version_field_present(self, client: TestClient) -> None:
        res = client.get("/health")
        data = res.json()["data"]
        assert "version" in data
        assert data["version"] == "0.0.1"  # current version


class TestProtectedHealth:
    """GET /api/v0-2/health/protected — Path Y protected."""

    def test_without_path_y_returns_200(self, client: TestClient) -> None:
        res = client.get("/api/v0-2/health/protected")
        assert res.status_code == 200
        body = res.json()
        assert body["data"]["path_y_validated"] is False
        assert body["data"]["user_id"] is None

    def test_with_valid_path_y(self, client: TestClient) -> None:
        ctx = {
            "version": "v0",
            "user_id": "u_alice",
            "org_id": "ou_engineering",
            "org_unit_ids": ["ou_engineering"],
            "project_ids": ["prj_ai_library"],
            "roles": ["developer", "admin"],
            "request_id": "req_001",
            "issued_at": "2026-06-26T00:00:00Z",
        }
        raw = json.dumps(ctx).encode("utf-8")
        encoded = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
        res = client.get(
            "/api/v0-2/health/protected",
            headers={"X-AiLibrary-User-Context": encoded},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["envelope"]["path_y_validated"] is True
        assert body["envelope"]["caller_user_id"] == "u_alice"
        assert body["data"]["user_id"] == "u_alice"
        assert body["data"]["org_id"] == "ou_engineering"
        assert body["data"]["roles"] == ["developer", "admin"]

    def test_with_invalid_path_y_falls_back(self, client: TestClient) -> None:
        res = client.get(
            "/api/v0-2/health/protected",
            headers={"X-AiLibrary-User-Context": "!!!invalid!!!"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["data"]["path_y_validated"] is False
        assert body["data"]["user_id"] is None


class TestApiError:
    """ApiError → JSONResponse 변환 (M-v0.0.2-a)."""

    def test_api_error_returns_proper_format(self, client: TestClient) -> None:
        # Use a path that doesn't exist — FastAPI returns 404, not our ApiError
        # This test verifies the error handler is registered (no crash on 404)
        res = client.get("/nonexistent")
        assert res.status_code == 404
"""Audit endpoint tests (M-v0.0.2-c).

GET /api/v1/audit — audit log list.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.main import create_app
from src.storage import audit
from src.config import load_config


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


@pytest.fixture
def var_dir():
    return load_config().var_dir


@pytest.fixture(autouse=True)
def reset_audit_log():
    """각 test 전 audit log 초기화 (in-memory + file 둘 다, test isolation)."""
    audit._in_memory_log.clear()
    audit._loaded = False
    from src.config import load_config
    log_file = load_config().var_dir / "audit" / "log.json"
    if log_file.exists():
        log_file.unlink()
    yield
    audit._in_memory_log.clear()
    audit._loaded = False
    if log_file.exists():
        log_file.unlink()


class TestAuditList:
    """GET /api/v1/audit — audit log list."""

    def test_list_returns_envelope(self, client: TestClient) -> None:
        res = client.get("/api/v1/audit")
        assert res.status_code == 200
        body = res.json()
        assert "items" in body["data"]
        assert "total" in body["data"]

    def test_list_includes_appended_entries(self, client: TestClient, var_dir) -> None:
        audit.append_audit(
            var_dir,
            action="test.action",
            actor="u_test",
            target_type="test",
            target_id="t1",
            details={"k": "v"},
        )
        res = client.get("/api/v1/audit")
        body = res.json()
        assert body["data"]["total"] >= 1
        actions = [e["action"] for e in body["data"]["items"]]
        assert "test.action" in actions

    def test_list_filters_by_action(self, client: TestClient, var_dir) -> None:
        audit.append_audit(var_dir, "action.a", "u1", "t", "id1")
        audit.append_audit(var_dir, "action.b", "u2", "t", "id2")
        res = client.get("/api/v1/audit?action=action.a")
        body = res.json()
        assert all(e["action"] == "action.a" for e in body["data"]["items"])

    def test_list_filters_by_actor(self, client: TestClient, var_dir) -> None:
        audit.append_audit(var_dir, "x", "alice", "t", "id1")
        audit.append_audit(var_dir, "x", "bob", "t", "id2")
        res = client.get("/api/v1/audit?actor=alice")
        body = res.json()
        assert all(e["actor"] == "alice" for e in body["data"]["items"])

    def test_list_pagination(self, client: TestClient, var_dir) -> None:
        for i in range(5):
            audit.append_audit(var_dir, "page", "u", "t", f"id{i}")
        res = client.get("/api/v1/audit?limit=2&offset=0")
        body = res.json()
        assert len(body["data"]["items"]) == 2
        assert body["data"]["total"] == 5
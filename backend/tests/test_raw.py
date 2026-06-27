"""Raw endpoint tests (M-v0.0.2-c).

GET /api/v1/raw + DELETE /api/v1/raw/{raw_id}
"""
from __future__ import annotations

import pytest
import uuid
from fastapi.testclient import TestClient

from src.main import create_app
from src.storage import raw as raw_storage
from src.config import load_config


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


@pytest.fixture
def var_dir():
    return load_config().var_dir


class TestRawList:
    """GET /api/v1/raw — raw list."""

    def test_list_returns_envelope(self, client: TestClient) -> None:
        res = client.get("/api/v1/raw")
        assert res.status_code == 200
        body = res.json()
        assert "items" in body["data"]
        assert "total" in body["data"]
        assert "limit" in body["data"]
        assert isinstance(body["data"]["items"], list)

    def test_list_filtered_by_source(self, client: TestClient, var_dir) -> None:
        # 2 raw 추가 (source=mock 1, source=test 1)
        raw_storage.append_raw(var_dir, "mock", {"title": "mock entry"})
        raw_storage.append_raw(var_dir, "test_source", {"title": "test entry"})

        res = client.get("/api/v1/raw?source=mock")
        assert res.status_code == 200
        for item in res.json()["data"]["items"]:
            assert item["source"] == "mock"

    def test_list_pagination(self, client: TestClient, var_dir) -> None:
        for i in range(5):
            raw_storage.append_raw(var_dir, "page_test", {"i": i})
        res = client.get("/api/v1/raw?source=page_test&limit=2&offset=0")
        body = res.json()
        assert body["data"]["total"] >= 5
        assert len(body["data"]["items"]) == 2


class TestRawDelete:
    """DELETE /api/v1/raw/{raw_id} — raw 삭제."""

    def test_delete_existing(self, client: TestClient, var_dir) -> None:
        raw_id = raw_storage.append_raw(var_dir, "del_test", {"title": "to delete"})
        res = client.delete(f"/api/v1/raw/{raw_id}")
        assert res.status_code == 200
        body = res.json()
        assert body["data"]["raw_id"] == raw_id
        assert body["data"]["deleted"] is True
        # 재삭제 시 404
        res2 = client.delete(f"/api/v1/raw/{raw_id}")
        assert res2.status_code == 404

    def test_delete_nonexistent_returns_404(self, client: TestClient) -> None:
        res = client.delete("/api/v1/raw/raw_nonexistent_xyz")
        assert res.status_code == 404

    def test_delete_writes_audit_entry(self, client: TestClient, var_dir) -> None:
        from src.storage import audit
        # audit log 초기화 (in-memory + file)
        audit._in_memory_log.clear()
        audit._loaded = False
        log_file = var_dir / "audit" / "log.json"
        if log_file.exists():
            log_file.unlink()
        raw_id = raw_storage.append_raw(var_dir, "audit_test", {"title": "x"})
        res = client.delete(f"/api/v1/raw/{raw_id}")
        assert res.status_code == 200
        entries = audit.list_audit(var_dir, action="raw.delete")
        assert len(entries) >= 1
        assert any(e["target_id"] == raw_id for e in entries)
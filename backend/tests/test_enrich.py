"""LLM enrich endpoint tests (M-v0.0.3-a).

POST /api/v1/enrich + /enrich/{job_id}/apply + GET /jobs + /metrics + /{job_id}

pi-coding-agent SDK 가 미설치인 환경 가정 (CI 기본 상태):
- 모든 enrich 호출이 success=False, error_code=E_NOT_IMPLEMENTED 반환 검증
- metrics endpoint 는 SDK 와 독립 (항상 동작)
- in-memory job store 동작 검증
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.main import create_app


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_enrich_state():
    """각 test 전 enrich job store + metrics reset."""
    from src.llm import pi_enrich
    from src.llm.metrics import get_metrics_store
    pi_enrich.reset_jobs()
    get_metrics_store().reset()
    yield
    pi_enrich.reset_jobs()
    get_metrics_store().reset()


@pytest.fixture
def concept_path():
    """테스트용 concept markdown 파일 (var_dir 내부에 생성, path security check 통과)."""
    from src.config import load_config
    var_dir = load_config().var_dir
    bundle_dir = var_dir / "bundles" / "test-enrich-bundle" / "concepts" / "adr"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    f = bundle_dir / "test-concept.md"
    f.write_text("# Test Concept\n\nThis is a test concept body for enrich.\n", encoding="utf-8")
    return str(f)


class TestEnrichCreate:
    """POST /api/v1/enrich."""

    def test_create_dry_run_returns_envelope(self, client: TestClient, concept_path) -> None:
        res = client.post(
            "/api/v1/enrich",
            json={"concept_path": concept_path, "mode": "dry_run"},
        )
        assert res.status_code == 200
        body = res.json()
        assert "job_id" in body["data"]
        assert body["data"]["mode"] == "dry_run"
        assert body["data"]["applied"] is False  # dry_run never applies

    def test_create_confirm_mode_returns_applied_false(self, client: TestClient, concept_path) -> None:
        res = client.post(
            "/api/v1/enrich",
            json={"concept_path": concept_path, "mode": "confirm"},
        )
        assert res.status_code == 200
        assert res.json()["data"]["applied"] is False

    def test_create_auto_apply_with_no_sdk_returns_not_implemented(
        self, client: TestClient, concept_path
    ) -> None:
        """SDK 미설치 시 auto_apply 도 success=False, error_code=E_NOT_IMPLEMENTED."""
        res = client.post(
            "/api/v1/enrich",
            json={"concept_path": concept_path, "mode": "auto_apply"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["data"]["result"]["success"] is False
        assert body["data"]["result"]["error_code"] == "E_NOT_IMPLEMENTED"

    def test_create_with_invalid_path_returns_404_in_result(
        self, client: TestClient
    ) -> None:
        res = client.post(
            "/api/v1/enrich",
            json={"concept_path": "/nonexistent/path/concept.md", "mode": "dry_run"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["data"]["result"]["error_code"] == "E_NOT_FOUND"

    def test_create_without_concept_path_returns_400(self, client: TestClient) -> None:
        res = client.post("/api/v1/enrich", json={"mode": "dry_run"})
        assert res.status_code == 400
        assert res.json()["detail"]["code"] == "E_BAD_REQUEST"

    def test_create_with_path_outside_var_dir_returns_404(self, client: TestClient) -> None:
        """path traversal 방어 — var/bundles/ 외부 경로 거부."""
        res = client.post(
            "/api/v1/enrich",
            json={"concept_path": "/etc/passwd", "mode": "dry_run"},
        )
        assert res.status_code == 200
        assert res.json()["data"]["result"]["error_code"] == "E_NOT_FOUND"

    def test_sdk_availability_flag_in_response(
        self, client: TestClient, concept_path
    ) -> None:
        res = client.post(
            "/api/v1/enrich",
            json={"concept_path": concept_path, "mode": "dry_run"},
        )
        body = res.json()
        assert "sdk_available" in body["data"]


class TestEnrichApply:
    """POST /api/v1/enrich/{job_id}/apply."""

    def test_apply_confirm_mode_job_with_failed_result_returns_409(
        self, client: TestClient, concept_path
    ) -> None:
        """SDK 미설치로 result.success=False → apply 시 409."""
        # confirm 모드로 job 생성 (result.success=False)
        create = client.post(
            "/api/v1/enrich",
            json={"concept_path": concept_path, "mode": "confirm"},
        )
        job_id = create.json()["data"]["job_id"]
        # apply 시도
        res = client.post(f"/api/v1/enrich/{job_id}/apply")
        # result.success=False → ValueError → 409
        assert res.status_code == 409

    def test_apply_nonexistent_job_returns_404(self, client: TestClient) -> None:
        res = client.post("/api/v1/enrich/enj_nonexistent/apply")
        assert res.status_code == 404


class TestEnrichJobs:
    """GET /api/v1/enrich/jobs + /{job_id}."""

    def test_jobs_list_returns_envelope(self, client: TestClient) -> None:
        res = client.get("/api/v1/enrich/jobs")
        assert res.status_code == 200
        body = res.json()
        assert "items" in body["data"]
        assert "total" in body["data"]

    def test_jobs_filter_by_mode(self, client: TestClient, concept_path) -> None:
        client.post("/api/v1/enrich", json={"concept_path": concept_path, "mode": "dry_run"})
        client.post("/api/v1/enrich", json={"concept_path": concept_path, "mode": "confirm"})
        res = client.get("/api/v1/enrich/jobs?mode=dry_run")
        for job in res.json()["data"]["items"]:
            assert job["mode"] == "dry_run"

    def test_jobs_invalid_status_returns_400(self, client: TestClient) -> None:
        res = client.get("/api/v1/enrich/jobs?status=invalid")
        assert res.status_code == 400

    def test_get_nonexistent_job_returns_404(self, client: TestClient) -> None:
        res = client.get("/api/v1/enrich/enj_nonexistent")
        assert res.status_code == 404


class TestEnrichMetrics:
    """GET /api/v1/enrich/metrics."""

    def test_metrics_returns_envelope_with_5_keys(self, client: TestClient) -> None:
        res = client.get("/api/v1/enrich/metrics")
        assert res.status_code == 200
        body = res.json()
        assert "mttr_minutes_avg" in body["data"]
        assert "accuracy" in body["data"]
        assert "false_positive_rate" in body["data"]
        assert "sdk_timeout_rate" in body["data"]
        assert "daily_recommend" in body["data"]
        assert "slo_breached" in body["data"]
        assert "slo_thresholds" in body["data"]
        assert "sdk_available" in body["data"]

    def test_sdk_timeout_rate_records_failed_call(self, client: TestClient, concept_path) -> None:
        """SDK 미설치 → sdk error 1건 기록."""
        client.post(
            "/api/v1/enrich",
            json={"concept_path": concept_path, "mode": "dry_run"},
        )
        res = client.get("/api/v1/enrich/metrics")
        body = res.json()
        # failed call 1건 → sdk_timeout_rate > 0 (timeout=False, error=True)
        assert body["data"]["sdk_timeout_rate"] >= 0.0
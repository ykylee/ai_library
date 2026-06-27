"""Monitoring endpoint tests (M-v0.0.2-c).

GET /api/v1/monitoring/alerts — 3-tier alerts.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.main import create_app


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


class TestListAlerts:
    """GET /api/v1/monitoring/alerts."""

    def test_returns_envelope_with_by_severity(self, client: TestClient) -> None:
        res = client.get("/api/v1/monitoring/alerts")
        assert res.status_code == 200
        body = res.json()
        assert "alerts" in body["data"]
        assert "total" in body["data"]
        assert "by_severity" in body["data"]
        assert set(body["data"]["by_severity"].keys()) == {"critical", "warning", "info"}

    def test_severity_filter(self, client: TestClient) -> None:
        res = client.get("/api/v1/monitoring/alerts?severity=info")
        assert res.status_code == 200
        for alert in res.json()["data"]["alerts"]:
            assert alert["severity"] == "info"

    def test_invalid_severity_returns_400(self, client: TestClient) -> None:
        res = client.get("/api/v1/monitoring/alerts?severity=invalid")
        assert res.status_code == 400
        assert res.json()["detail"]["code"] == "E_BAD_REQUEST"

    def test_alerts_sorted_by_severity(self, client: TestClient) -> None:
        res = client.get("/api/v1/monitoring/alerts")
        alerts = res.json()["data"]["alerts"]
        sev_order = {"critical": 0, "warning": 1, "info": 2}
        for i in range(len(alerts) - 1):
            assert sev_order[alerts[i]["severity"]] <= sev_order[alerts[i + 1]["severity"]]

    def test_critical_alert_when_source_has_auth_failures(self, client: TestClient) -> None:
        from src.sources.registry import get_source
        src = get_source("mock")
        original = src.auth_failures
        src.auth_failures = 3
        try:
            res = client.get("/api/v1/monitoring/alerts?severity=critical")
            body = res.json()
            target_names = {a["target"] for a in body["data"]["alerts"]}
            assert "mock" in target_names
        finally:
            src.auth_failures = original
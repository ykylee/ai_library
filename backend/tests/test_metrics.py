"""LLM enrich metrics store unit tests (M-v0.0.3-a).

MetricsStore 의 5 metrics 동작 단위 검증.
"""
from __future__ import annotations

import pytest

from src.llm.metrics import (
    MetricsStore,
    SLO_ACCURACY,
    SLO_DAILY_RECOMMEND,
    SLO_FALSE_POSITIVE,
    SLO_MTTR_MINUTES,
    SLO_SDK_TIMEOUT_RATE,
)


@pytest.fixture
def store():
    return MetricsStore()


class TestMetricsRecordCall:
    """SDK 호출 기록."""

    def test_initial_snapshot_is_zero(self, store: MetricsStore) -> None:
        snap = store.snapshot()
        assert snap.mttr_minutes_avg == 0.0
        assert snap.accuracy == 0.0
        assert snap.false_positive_rate == 0.0
        assert snap.sdk_timeout_rate == 0.0
        assert snap.daily_recommend == 0
        assert snap.slo_breached == []

    def test_record_success_call(self, store: MetricsStore) -> None:
        store.record_call(success=True, timeout=False, error=False)
        snap = store.snapshot()
        assert snap.sdk_timeout_rate == 0.0  # no timeouts

    def test_record_timeout_increments_rate(self, store: MetricsStore) -> None:
        store.record_call(success=False, timeout=True, error=False)
        snap = store.snapshot()
        assert snap.sdk_timeout_rate == 1.0  # 1/1 = 100%

    def test_record_error_increments_total(self, store: MetricsStore) -> None:
        store.record_call(success=False, timeout=False, error=True)
        store.record_call(success=True, timeout=False, error=False)
        snap = store.snapshot()
        # 1/2 total, 0 timeouts
        assert snap.sdk_timeout_rate == 0.0


class TestMetricsRecordApply:
    """Apply 기록 + MTTR."""

    def test_record_apply_increments_mttr(self, store: MetricsStore) -> None:
        store.record_apply(mttr_minutes=15.0)
        store.record_apply(mttr_minutes=25.0)
        snap = store.snapshot()
        assert snap.mttr_minutes_avg == 20.0  # (15+25)/2

    def test_mttr_breach_flagged(self, store: MetricsStore) -> None:
        store.record_apply(mttr_minutes=SLO_MTTR_MINUTES + 5)
        snap = store.snapshot()
        assert "mttr_minutes" in snap.slo_breached

    def test_mttr_within_slo_not_breached(self, store: MetricsStore) -> None:
        store.record_apply(mttr_minutes=SLO_MTTR_MINUTES - 5)
        snap = store.snapshot()
        assert "mttr_minutes" not in snap.slo_breached


class TestMetricsReject:
    """Reject 기록 → accuracy/false_positive 계산."""

    def test_record_reject_increments_false_positive(self, store: MetricsStore) -> None:
        store.record_apply(mttr_minutes=10.0)  # 1 applied
        store.record_reject()  # 1 rejected
        snap = store.snapshot()
        # 1 rejected / 2 feedback = 50% → breached (SLO 5%)
        assert snap.false_positive_rate == 0.5
        assert snap.accuracy == 0.5
        assert "false_positive" in snap.slo_breached
        assert "accuracy" in snap.slo_breached


class TestMetricsDaily:
    """일일 recommend 카운트."""

    def test_daily_recommend_increments(self, store: MetricsStore) -> None:
        for _ in range(3):
            store.record_apply(mttr_minutes=10.0)
        snap = store.snapshot()
        assert snap.daily_recommend == 3

    def test_daily_breach_flagged(self, store: MetricsStore) -> None:
        for _ in range(SLO_DAILY_RECOMMEND + 5):
            store.record_apply(mttr_minutes=10.0)
        snap = store.snapshot()
        assert "daily_recommend" in snap.slo_breached


class TestMetricsReset:
    """Reset 동작."""

    def test_reset_clears_state(self, store: MetricsStore) -> None:
        store.record_call(success=False, timeout=True, error=False)
        store.record_apply(mttr_minutes=10.0)
        store.reset()
        snap = store.snapshot()
        assert snap.mttr_minutes_avg == 0.0
        assert snap.sdk_timeout_rate == 0.0
        assert snap.daily_recommend == 0


def test_slo_constants_are_sane():
    """SLO 상수가 reasonable 한지 sanity check."""
    assert 0 < SLO_ACCURACY < 1.0
    assert 0 < SLO_FALSE_POSITIVE < 1.0
    assert 0 < SLO_SDK_TIMEOUT_RATE < 1.0
    assert SLO_MTTR_MINUTES > 0
    assert SLO_DAILY_RECOMMEND > 0
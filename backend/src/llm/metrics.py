"""LLM enrich metrics store (M-v0.0.3-a).

5 metrics (per roadmap §M-v0.0.3 spec):
1. MTTR < 30분 : job created_at ~ applied_at 의 평균 (분)
2. accuracy ≥ 70% : apply 후 false positive 비율 역수 (수동 검증 필요, baseline 0.0)
3. false positive ≤ 5% : 사용자 reject 비율 (수동 검증 필요, baseline 0.0)
4. pi_sdk_timeout ≤ 1% : SDK 호출 중 timeout/error 비율
5. 일 ≤ 50 recommend : 일일 dry_run + confirm + auto_apply 합계

본 모듈은 in-memory counter + accumulator. file persist 는 M-v0.0.3-b 에서 추가.
"""
from __future__ import annotations

import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any


# 5 metrics 의 SLO 임계값 (per roadmap §M-v0.0.3)
SLO_MTTR_MINUTES = 30  # 평균 MTTR (분)
SLO_ACCURACY = 0.70  # 70% 이상
SLO_FALSE_POSITIVE = 0.05  # 5% 이하
SLO_SDK_TIMEOUT_RATE = 0.01  # 1% 이하
SLO_DAILY_RECOMMEND = 50  # 일 50건 이하


@dataclass
class MetricsSnapshot:
    """현재 시점의 metrics snapshot."""

    mttr_minutes_avg: float  # 0.0 if no completed jobs
    accuracy: float  # 0.0 if no feedback
    false_positive_rate: float
    sdk_timeout_rate: float
    daily_recommend: int  # today count
    slo_breached: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "mttr_minutes_avg": round(self.mttr_minutes_avg, 2),
            "accuracy": round(self.accuracy, 4),
            "false_positive_rate": round(self.false_positive_rate, 4),
            "sdk_timeout_rate": round(self.sdk_timeout_rate, 4),
            "daily_recommend": self.daily_recommend,
            "slo_breached": self.slo_breached,
            "slo_thresholds": {
                "mttr_minutes_max": SLO_MTTR_MINUTES,
                "accuracy_min": SLO_ACCURACY,
                "false_positive_max": SLO_FALSE_POSITIVE,
                "sdk_timeout_rate_max": SLO_SDK_TIMEOUT_RATE,
                "daily_recommend_max": SLO_DAILY_RECOMMEND,
            },
        }


class MetricsStore:
    """Thread-safe in-memory metrics store."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._total_calls: int = 0
        self._sdk_timeouts: int = 0
        self._sdk_errors: int = 0
        self._applied_count: int = 0  # mode = confirm/auto_apply + applied_at
        self._rejected_count: int = 0  # 수동 reject (M-v0.0.3-b 에서 API, baseline 0)
        self._mttr_total_minutes: float = 0.0
        self._mttr_samples: int = 0
        self._daily: dict[str, int] = defaultdict(int)  # YYYY-MM-DD → count

    def record_call(self, *, success: bool, timeout: bool, error: bool) -> None:
        """SDK 호출 1건 기록.

        - success=False, timeout=True → sdk_timeout
        - success=False, error=True → sdk_error
        - success=True → success
        """
        with self._lock:
            self._total_calls += 1
            if timeout:
                self._sdk_timeouts += 1
            if error and not timeout:
                self._sdk_errors += 1

    def record_apply(self, *, mttr_minutes: float) -> None:
        """apply 1건 + MTTR 기록."""
        today = date.today().isoformat()
        with self._lock:
            self._applied_count += 1
            self._mttr_total_minutes += mttr_minutes
            self._mttr_samples += 1
            self._daily[today] += 1

    def record_reject(self) -> None:
        """사용자 reject 1건 (M-v0.0.3-b API)."""
        with self._lock:
            self._rejected_count += 1

    def snapshot(self) -> MetricsSnapshot:
        """현재 snapshot."""
        with self._lock:
            total = self._total_calls
            timeout_rate = self._sdk_timeouts / total if total > 0 else 0.0
            applied = self._applied_count
            rejected = self._rejected_count
            feedback_total = applied + rejected
            fp_rate = rejected / feedback_total if feedback_total > 0 else 0.0
            accuracy = 1.0 - fp_rate if feedback_total > 0 else 0.0
            mttr_avg = (
                self._mttr_total_minutes / self._mttr_samples
                if self._mttr_samples > 0
                else 0.0
            )
            today_count = self._daily.get(date.today().isoformat(), 0)

        breached: list[str] = []
        if mttr_avg > SLO_MTTR_MINUTES:
            breached.append("mttr_minutes")
        if feedback_total > 0 and accuracy < SLO_ACCURACY:
            breached.append("accuracy")
        if feedback_total > 0 and fp_rate > SLO_FALSE_POSITIVE:
            breached.append("false_positive")
        if total > 0 and timeout_rate > SLO_SDK_TIMEOUT_RATE:
            breached.append("sdk_timeout_rate")
        if today_count > SLO_DAILY_RECOMMEND:
            breached.append("daily_recommend")

        return MetricsSnapshot(
            mttr_minutes_avg=mttr_avg,
            accuracy=accuracy,
            false_positive_rate=fp_rate,
            sdk_timeout_rate=timeout_rate,
            daily_recommend=today_count,
            slo_breached=breached,
        )

    def reset(self) -> None:
        """전체 reset (test isolation 용)."""
        with self._lock:
            self._total_calls = 0
            self._sdk_timeouts = 0
            self._sdk_errors = 0
            self._applied_count = 0
            self._rejected_count = 0
            self._mttr_total_minutes = 0.0
            self._mttr_samples = 0
            self._daily.clear()


# module-level singleton (in-memory)
_store = MetricsStore()


def get_metrics_store() -> MetricsStore:
    """Process-wide metrics store singleton."""
    return _store


__all__ = [
    "MetricsStore",
    "MetricsSnapshot",
    "get_metrics_store",
    "SLO_MTTR_MINUTES",
    "SLO_ACCURACY",
    "SLO_FALSE_POSITIVE",
    "SLO_SDK_TIMEOUT_RATE",
    "SLO_DAILY_RECOMMEND",
]
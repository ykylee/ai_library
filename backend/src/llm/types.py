"""LLM enrich types (M-v0.0.3-a).

enrich workflow 의 모든 type/dataclass 정의:
- EnrichMode: 3-mode confirm workflow 의 enum
- EnrichResult: enrich 호출 결과 (success/error + confidence + metadata)
- EnrichJob: 진행 중인 enrich job (state machine: queued → running → completed/failed)
- ConceptMetadata: enrich 가 생성하는 concept 부가 정보 (8종 OKF field)

본 모듈은 pi-coding-agent SDK 와 독립적 (SDK 없어도 import 가능).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class EnrichMode(str, Enum):
    """3-mode confirm workflow (M-v0.0.3-a spec).

    - dry_run: enrich 실행하되 결과 preview 만 (실제 metadata write 안 함)
    - confirm: caller 가 명시적으로 apply 호출해야 실제 write (default)
    - auto_apply: confidence >= threshold 면 자동 write (M-v0.0.3-a 의 default threshold = 0.9)

    api 의 ?mode=... query param 으로 caller 가 선택.
    """

    DRY_RUN = "dry_run"
    CONFIRM = "confirm"
    AUTO_APPLY = "auto_apply"

    @classmethod
    def parse(cls, value: str | None) -> "EnrichMode":
        """caller string → EnrichMode. invalid 시 CONFIRM (default)."""
        if value is None:
            return cls.CONFIRM
        try:
            return cls(value)
        except ValueError:
            return cls.CONFIRM


class EnrichStatus(str, Enum):
    """Job state machine (queued → running → completed/failed/cancelled)."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ConceptMetadata:
    """Pi SDK 가 enrich 한 concept metadata (8종 OKF field).

    본 repo 의 concept markdown 에는 title / body 만 있고, ADR/runbook 의 frontmatter
    metadata (decision / status / date / owner) 가 비어있는 경우가 많음. enrich 가 보강.
    """

    # OKF concept 공통 (8종 모두)
    title: str | None = None
    summary: str | None = None  # 1-2 줄 abstract
    tags: list[str] = field(default_factory=list)

    # ADR-only (optional)
    decision: str | None = None
    status: str | None = None  # proposed / accepted / deprecated / superseded
    date: str | None = None
    deciders: list[str] = field(default_factory=list)

    # runbook-only (optional)
    trigger: str | None = None
    steps: list[str] = field(default_factory=list)

    # postmortem-only (optional)
    incident_date: str | None = None
    root_cause: str | None = None
    resolution: str | None = None

    # confidence (0.0 ~ 1.0)
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict (None field 제외)."""
        d: dict[str, Any] = {}
        for k, v in self.__dict__.items():
            if v is None or v == [] or v == 0.0:
                continue
            d[k] = list(v) if isinstance(v, list) else v
        return d


@dataclass
class EnrichResult:
    """enrich_concept_metadata 호출 결과.

    - success=True: Pi SDK 가 metadata 생성 성공
    - success=False: error (SDK timeout / invalid input / etc.)
    """

    success: bool
    metadata: ConceptMetadata
    error_code: str | None = None  # E_SDK_TIMEOUT / E_INVALID_INPUT / E_INTERNAL
    error_message: str | None = None
    duration_ms: int = 0
    mode: str = "sdk"  # sdk / rpc / standalone (M-v0.0.3-a scope: sdk only)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "success": self.success,
            "metadata": self.metadata.to_dict(),
            "duration_ms": self.duration_ms,
            "mode": self.mode,
        }
        if self.error_code is not None:
            d["error_code"] = self.error_code
        if self.error_message is not None:
            d["error_message"] = self.error_message
        return d


@dataclass
class EnrichJob:
    """진행 중이거나 완료된 enrich job (in-memory store).

    state machine: queued → running → completed/failed/cancelled
    """

    job_id: str
    concept_path: str
    mode: EnrichMode
    status: EnrichStatus = EnrichStatus.QUEUED
    prompt_template: str | None = None
    result: EnrichResult | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    created_by: str = "anonymous"
    applied_at: str | None = None
    cancelled_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "job_id": self.job_id,
            "concept_path": self.concept_path,
            "mode": self.mode.value,
            "status": self.status.value,
            "created_at": self.created_at,
            "created_by": self.created_by,
        }
        if self.result is not None:
            d["result"] = self.result.to_dict()
        if self.applied_at is not None:
            d["applied_at"] = self.applied_at
        if self.cancelled_at is not None:
            d["cancelled_at"] = self.cancelled_at
        return d


def new_job_id() -> str:
    """새 job ID 생성."""
    return f"enj_{uuid.uuid4().hex[:12]}"


__all__ = [
    "EnrichMode",
    "EnrichStatus",
    "ConceptMetadata",
    "EnrichResult",
    "EnrichJob",
    "new_job_id",
]
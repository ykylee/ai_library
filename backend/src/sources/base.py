"""Source plugin abstract base (M-v0.3.0-alpha placeholder).

DevHub umbrella §3.8 (SourceMeta) + §3.7 (data normalization pipeline) 정합.

각 plugin 은 SourcePlugin 상속 + 4 method 구현:
- meta() -> SourceMeta: source 식별 + body_template
- pull() -> AsyncIterator[RawEntry]: 외부 시스템에서 1차 raw fetch
- normalize(raw) -> NormalizedEntry: §3.7 normalization pipeline
- health() -> HealthStatus: §3.7.6.5 auth failure monitoring

M-v0.3.0+ 부터 실제 구현.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncIterator


@dataclass(frozen=True)
class SourceMeta:
    """외부 시스템 source 메타 정보 (DevHub umbrella §3.8.1)."""

    name: str  # 예: "gitea_repo_pull"
    version: str  # 예: "0.3.0"
    body_template: str  # OKF concept 변환용 Jinja2 template
    health_url: str | None = None


@dataclass(frozen=True)
class RawEntry:
    """1차 raw data entry (DevHub umbrella §3.8.2)."""

    source: str
    external_id: str
    fetched_at: str  # ISO 8601
    body: Any  # source-specific (dict, str, bytes 등)
    size_bytes: int
    sha256: str


@dataclass(frozen=True)
class NormalizedEntry:
    """정규화된 entry (DevHub umbrella §3.7.4)."""

    source: str
    external_id: str
    concept_type: str  # OKF 8종 type enum 중 1
    payload: dict[str, Any]


@dataclass(frozen=True)
class HealthStatus:
    """source plugin health (DevHub umbrella §3.7.6.5)."""

    name: str
    healthy: bool
    last_sync: str  # ISO 8601
    items_count: int
    auth_failures: int  # 최근 1시간 401/403 count


class SourcePlugin(ABC):
    """Source plugin abstract base."""

    @abstractmethod
    def meta(self) -> SourceMeta: ...

    @abstractmethod
    async def pull(self) -> AsyncIterator[RawEntry]: ...

    @abstractmethod
    def normalize(self, raw: RawEntry) -> NormalizedEntry: ...

    @abstractmethod
    def health(self) -> HealthStatus: ...

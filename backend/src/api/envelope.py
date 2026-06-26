"""API envelope (web frontend `EnvelopeMeta` / `Envelope<T>` 정합).

모든 endpoint response = `{ envelope: EnvelopeMeta, data: T }` 형식.
envelope middleware 가 request.state 에 request_id + path_y context 주입,
endpoint 가 `EnvelopeContext.wrap(data)` 호출하여 최종 JSON 반환.

web frontend 호환 (types.ts Envelope / EnvelopeMeta 1:1):
- envelope.request_id : UUID4 string
- envelope.timestamp : ISO 8601
- envelope.api_version : "v0-2"
- envelope.caller_user_id : string | null  (Path Y 의 user_id 또는 null)
- envelope.path_y_validated : boolean  (Path Y header 가 정상 decode 됐는지)
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from .path_y import PathYUserContext


class EnvelopeMeta(BaseModel):
    """Envelope metadata (web frontend EnvelopeMeta 1:1 정합)."""

    request_id: str
    timestamp: str
    api_version: str = "v0-2"
    caller_user_id: str | None = None
    path_y_validated: bool = False


class Envelope(BaseModel):
    """Envelope response wrapper (`{ envelope, data }`)."""

    envelope: EnvelopeMeta
    data: Any = None


class EnvelopeContext:
    """Per-request envelope metadata holder (FastAPI dependency).

    middleware 가 request.state 에 주입 → endpoint 가 dependency 로 수신.
    endpoint return 시 `EnvelopeContext.wrap(data)` 호출.
    """

    def __init__(
        self,
        request_id: str,
        path_y: PathYUserContext | None,
        timestamp: str | None = None,
    ) -> None:
        self.request_id = request_id
        self.path_y = path_y
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()

    @classmethod
    def new(cls, path_y: PathYUserContext | None = None) -> "EnvelopeContext":
        """새 request 시작 시 envelope context 생성 (middleware 가 호출)."""
        return cls(request_id=str(uuid4()), path_y=path_y)

    def meta(self) -> EnvelopeMeta:
        """Build EnvelopeMeta from current context."""
        return EnvelopeMeta(
            request_id=self.request_id,
            timestamp=self.timestamp,
            api_version="v0-2",
            caller_user_id=self.path_y.user_id if self.path_y else None,
            path_y_validated=self.path_y is not None,
        )

    def wrap(self, data: Any) -> dict[str, Any]:
        """Wrap endpoint data in envelope."""
        return Envelope(envelope=self.meta(), data=data).model_dump(mode="json")


# 모듈 export
__all__ = ["EnvelopeMeta", "Envelope", "EnvelopeContext"]
"""Path Y caller-provided user context (ADR-0001 §2.3 standalone 정책).

본 repo 는 OIDC / SSO 인증 게이트웨이 없음. 대신 caller 가 직접 `X-AiLibrary-User-Context`
HTTP header 로 user context 를 주입. backend 는 signature / payload 를 검증하지 **않음** (trust the caller).

header 형식 = base64url(JSON) (web frontend `path-y.ts` 의 `encodePathY` 정합).
decode 실패 시 None 반환 — 401 raise ❌ (내부 trusted 환경 가정).
"""
from __future__ import annotations

import base64
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class PathYUserContext:
    """Caller-provided user context (8 field, OKF v0.1 spec §3.6.1 정합)."""

    version: str
    user_id: str
    org_id: str
    org_unit_ids: list[str]
    project_ids: list[str]
    roles: list[str]
    request_id: str
    issued_at: str


def parse_path_y(header_value: str | None) -> PathYUserContext | None:
    """`X-AiLibrary-User-Context` header decode → PathYUserContext.

    base64url(JSON) decode. invalid input 시 None 반환 (raise ❌).
    trust the caller (ADR-0001 §2.3).
    """
    if not header_value:
        return None
    try:
        # base64url → base64 padding 추가
        padded = header_value + "=" * (-len(header_value) % 4)
        raw = base64.urlsafe_b64decode(padded.encode("ascii"))
        data = json.loads(raw.decode("utf-8"))
        return PathYUserContext(
            version=data["version"],
            user_id=data["user_id"],
            org_id=data["org_id"],
            org_unit_ids=list(data.get("org_unit_ids", [])),
            project_ids=list(data.get("project_ids", [])),
            roles=list(data.get("roles", [])),
            request_id=data["request_id"],
            issued_at=data["issued_at"],
        )
    except (ValueError, KeyError, TypeError, UnicodeDecodeError, json.JSONDecodeError):
        return None
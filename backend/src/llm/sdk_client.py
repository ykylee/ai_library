"""Pi SDK client wrapper (M-v0.0.3-a).

pi-coding-agent SDK 를 import 해서 concept enrichment 호출.
SDK 가 미설치 (optional dep) 시 graceful skip + E_NOT_IMPLEMENTED 반환.

본 모듈의 책임:
- import 시도 + 실패 시 (ImportError) sentinel return
- SDK 의 generate/enrich 호출을 wrap → ConceptMetadata 로 변환
- timeout / error 처리를 metrics store 에 기록

M-v0.0.3-a scope: sdk mode only.
M-v0.0.3-b 에서 rpc mode / standalone mode 추가.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any

from .metrics import get_metrics_store
from .types import ConceptMetadata, EnrichResult


logger = logging.getLogger("ai_library.llm.sdk_client")


def is_sdk_available() -> bool:
    """pi-coding-agent SDK 가 import 가능한지 확인."""
    try:
        import pi_coding_agent  # noqa: F401

        return True
    except ImportError:
        return False


def _parse_metadata_from_response(text: str) -> ConceptMetadata:
    """SDK 응답 text → ConceptMetadata.

    pi-coding-agent 응답 형식 (M-v0.0.3-a 가정):
    - 자유 형식 markdown 또는 structured dict
    - 본 구현은 naive regex 파싱 (M-v0.0.3-b 에서 structured JSON 으로 교체)

    field 추출 우선순위:
    - "Title:" / "title:" → title
    - "Summary:" / "summary:" → summary (다음 줄 ~ 빈 줄 전까지)
    - "Tags:" / "tags:" → tags (comma-separated)
    - "Decision:" / "Status:" / "Date:" / "Deciders:" → ADR field
    """
    md = ConceptMetadata()

    # title (first heading 또는 "Title:" line)
    title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE) or re.search(
        r"(?:^|\n)Title:\s*(.+?)(?:\n|$)", text
    )
    if title_match:
        md.title = title_match.group(1).strip()

    # summary
    summary_match = re.search(
        r"(?:^|\n)Summary:\s*(.+?)(?:\n\n|\n[A-Z][a-z]+:|\Z)",
        text,
        re.DOTALL,
    )
    if summary_match:
        md.summary = summary_match.group(1).strip()

    # tags
    tags_match = re.search(r"(?:^|\n)Tags:\s*(.+?)(?:\n|$)", text)
    if tags_match:
        md.tags = [t.strip() for t in tags_match.group(1).split(",") if t.strip()]

    # ADR fields (optional)
    for field_name in ("decision", "status", "date"):
        m = re.search(rf"(?:^|\n){field_name.capitalize()}:\s*(.+?)(?:\n|$)", text)
        if m:
            setattr(md, field_name, m.group(1).strip())

    deciders_match = re.search(r"(?:^|\n)Deciders:\s*(.+?)(?:\n|$)", text)
    if deciders_match:
        md.deciders = [d.strip() for d in deciders_match.group(1).split(",") if d.strip()]

    # confidence: M-v0.0.3-a baseline = 0.8 (SDK 응답에 명시 없으면)
    md.confidence = 0.8

    return md


async def call_sdk(
    concept_body: str,
    prompt_template: str | None = None,
    timeout_seconds: float = 30.0,
) -> EnrichResult:
    """pi-coding-agent SDK 호출하여 concept enrichment.

    - SDK 미설치 → success=False, error_code="E_NOT_IMPLEMENTED"
    - SDK timeout → success=False, error_code="E_SDK_TIMEOUT"
    - 그 외 error → success=False, error_code="E_INTERNAL"
    - 정상 → success=True, metadata 채워짐
    """
    started = datetime.now(timezone.utc)
    metrics = get_metrics_store()

    if not is_sdk_available():
        metrics.record_call(success=False, timeout=False, error=True)
        return EnrichResult(
            success=False,
            metadata=ConceptMetadata(),
            error_code="E_NOT_IMPLEMENTED",
            error_message=(
                "pi-coding-agent SDK not installed. "
                "Run `pip install -e .[pi]` to enable M-v0.0.3-a sdk mode."
            ),
            mode="sdk",
        )

    try:
        import pi_coding_agent

        # SDK 호출 (M-v0.0.3-a: 동기 호출 — async SDK 는 M-v0.0.3-b 에서 wrap)
        sdk = pi_coding_agent
        prompt = prompt_template or _default_prompt(concept_body)
        response_text = sdk.generate(prompt=prompt, max_tokens=1024)
    except TimeoutError as e:
        elapsed = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
        metrics.record_call(success=False, timeout=True, error=False)
        return EnrichResult(
            success=False,
            metadata=ConceptMetadata(),
            error_code="E_SDK_TIMEOUT",
            error_message=f"SDK timeout after {timeout_seconds}s: {e}",
            duration_ms=elapsed,
            mode="sdk",
        )
    except Exception as e:
        elapsed = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
        logger.exception("pi-coding-agent SDK call failed")
        metrics.record_call(success=False, timeout=False, error=True)
        return EnrichResult(
            success=False,
            metadata=ConceptMetadata(),
            error_code="E_INTERNAL",
            error_message=f"SDK call failed: {type(e).__name__}: {e}",
            duration_ms=elapsed,
            mode="sdk",
        )

    elapsed = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
    metadata = _parse_metadata_from_response(str(response_text))
    metrics.record_call(success=True, timeout=False, error=False)
    return EnrichResult(
        success=True,
        metadata=metadata,
        duration_ms=elapsed,
        mode="sdk",
    )


def _default_prompt(concept_body: str) -> str:
    """기본 enrich prompt template."""
    return (
        "Extract structured metadata from the following concept document.\n"
        "Format your response as:\n"
        "Title: <one-line title>\n"
        "Summary: <1-2 sentence abstract>\n"
        "Tags: <comma-separated tags>\n"
        "Decision: <for ADR type>\n"
        "Status: <for ADR type>\n"
        "Date: <for ADR type>\n"
        "Deciders: <for ADR type>\n\n"
        f"Concept body:\n{concept_body[:4000]}"
    )


__all__ = ["is_sdk_available", "call_sdk", "_parse_metadata_from_response"]
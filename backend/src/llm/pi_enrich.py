"""Pi LLM enrich agent (M-v0.0.3-a).

3-mode confirm workflow 의 오케스트레이션:
- dry_run: enrich 실행하되 결과 preview 만 (실제 metadata write 안 함)
- confirm: caller 가 명시적으로 apply 호출해야 실제 write (default)
- auto_apply: confidence >= threshold 면 자동 write (M-v0.0.3-a default = 0.9)

job lifecycle:
1. caller 가 POST /api/v1/enrich 호출 → job_id 발급 + 즉시 enrich 실행
   - dry_run: result 즉시 반환
   - confirm: result 와 함께 "applied=false" 반환, caller 가 /apply 호출해야 write
   - auto_apply: confidence >= 0.9 면 즉시 write, 아니면 confirm 처럼 대기
2. caller 가 POST /api/v1/enrich/{job_id}/apply 호출 → confirm 모드 job 에 한해 write
3. apply 시 audit log + metrics 기록

SDK 미설치 시 모든 호출이 success=False, error_code=E_NOT_IMPLEMENTED 반환.
"""
from __future__ import annotations

import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..storage import audit, write_json
from .metrics import get_metrics_store
from .sdk_client import call_sdk, is_sdk_available
from .types import (
    ConceptMetadata,
    EnrichJob,
    EnrichMode,
    EnrichResult,
    EnrichStatus,
    new_job_id,
)


# auto_apply confidence threshold (M-v0.0.3-a spec)
AUTO_APPLY_CONFIDENCE_THRESHOLD = 0.9


# in-memory job store (M-v0.0.3-b 에서 file persist 추가)
_lock = threading.Lock()
_jobs: dict[str, EnrichJob] = {}


def list_jobs(
    status: EnrichStatus | None = None,
    mode: EnrichMode | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[EnrichJob]:
    """Job list 조회."""
    with _lock:
        jobs = list(_jobs.values())
    if status is not None:
        jobs = [j for j in jobs if j.status == status]
    if mode is not None:
        jobs = [j for j in jobs if j.mode == mode]
    jobs.sort(key=lambda j: j.created_at, reverse=True)
    return jobs[offset : offset + limit]


def count_jobs() -> int:
    """Total job count."""
    with _lock:
        return len(_jobs)


def get_job(job_id: str) -> EnrichJob | None:
    """Job 조회."""
    with _lock:
        return _jobs.get(job_id)


def _read_concept_body(concept_path: str) -> str | None:
    """Concept markdown file read. None if not exists or path invalid.

    보안: path traversal 방어 — 절대경로 + var/bundles/ prefix check.
    """
    from ..config import load_config

    config = load_config()
    var_dir = config.var_dir.resolve()
    p = Path(concept_path).resolve()
    try:
        p.relative_to(var_dir)
    except ValueError:
        return None  # var/ 외부 경로 거부
    if not p.exists() or not p.is_file():
        return None
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return None


def _write_concept_metadata(concept_path: str, metadata: ConceptMetadata) -> bool:
    """Concept file 에 metadata 를 frontmatter 로 write (atomic).

    기존 content 보존 + frontmatter 추가/갱신.
    Returns: write 성공 여부.
    """
    from ..config import load_config

    config = load_config()
    var_dir = config.var_dir.resolve()
    p = Path(concept_path).resolve()
    try:
        p.relative_to(var_dir)
    except ValueError:
        return False
    if not p.exists() or not p.is_file():
        return False

    existing = p.read_text(encoding="utf-8")
    frontmatter_lines = ["---"]
    for key, value in metadata.to_dict().items():
        if isinstance(value, list):
            frontmatter_lines.append(f"{key}: [{', '.join(str(v) for v in value)}]")
        elif isinstance(value, str):
            escaped = value.replace('"', '\\"')
            frontmatter_lines.append(f'{key}: "{escaped}"')
        elif isinstance(value, (int, float)):
            frontmatter_lines.append(f"{key}: {value}")
    frontmatter_lines.append("---\n")

    # 기존 frontmatter 제거 (있으면)
    body = existing
    if body.startswith("---\n"):
        end = body.find("\n---\n", 4)
        if end > 0:
            body = body[end + 5 :]

    new_content = "\n".join(frontmatter_lines) + body
    try:
        write_json_to_path = None
        # atomic write via tmp + rename
        import tempfile
        import os

        fd, tmp_path = tempfile.mkstemp(dir=str(p.parent), prefix=f".{p.name}.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(new_content)
            os.replace(tmp_path, p)
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise
        return True
    except OSError:
        return False


def reset_jobs() -> None:
    """전체 job 초기화 (test isolation 용)."""
    global _jobs
    with _lock:
        _jobs = {}


async def create_enrich_job(
    concept_path: str,
    mode: EnrichMode,
    prompt_template: str | None = None,
    actor: str = "anonymous",
    var_dir: Path | None = None,
) -> EnrichJob:
    """새 enrich job 생성 + 즉시 enrich 실행.

    - dry_run: enrich 실행 + result 채움 (write 안 함)
    - confirm: enrich 실행 + result 채움 (write 안 함, apply 대기)
    - auto_apply: enrich 실행 + confidence >= threshold 면 즉시 write
    """
    job_id = new_job_id()
    job = EnrichJob(
        job_id=job_id,
        concept_path=concept_path,
        mode=mode,
        prompt_template=prompt_template,
        created_by=actor,
    )

    body = _read_concept_body(concept_path)
    if body is None:
        job.status = EnrichStatus.FAILED
        job.result = EnrichResult(
            success=False,
            metadata=ConceptMetadata(),
            error_code="E_NOT_FOUND",
            error_message=f"concept not found or invalid path: {concept_path}",
        )
    else:
        job.status = EnrichStatus.RUNNING
        result = await call_sdk(body, prompt_template=prompt_template)
        job.result = result
        if not result.success:
            job.status = EnrichStatus.FAILED
        elif mode == EnrichMode.AUTO_APPLY and result.metadata.confidence >= AUTO_APPLY_CONFIDENCE_THRESHOLD:
            # auto_apply: 즉시 write
            applied = _write_concept_metadata(concept_path, result.metadata)
            if applied:
                job.status = EnrichStatus.COMPLETED
                job.applied_at = datetime.now(timezone.utc).isoformat()
                _record_metrics_and_audit(
                    job=job,
                    action="enrich.auto_apply",
                    actor=actor,
                    var_dir=var_dir,
                )
            else:
                job.status = EnrichStatus.FAILED
                job.result.error_code = "E_INTERNAL"
                job.result.error_message = "metadata write failed"
        elif mode == EnrichMode.DRY_RUN:
            job.status = EnrichStatus.COMPLETED
        else:  # CONFIRM
            job.status = EnrichStatus.COMPLETED  # result ready, apply 대기

    with _lock:
        _jobs[job_id] = job
    return job


def apply_job(job_id: str, actor: str = "anonymous", var_dir: Path | None = None) -> EnrichJob:
    """confirm 모드 job 을 actual write.

    - 이미 applied 이거나 cancelled → idempotent error
    - result 없거나 failed → error
    - 성공 시 metadata write + audit + metrics 기록
    """
    with _lock:
        job = _jobs.get(job_id)
    if job is None:
        raise KeyError(f"job not found: {job_id}")
    if job.applied_at is not None:
        raise ValueError(f"job already applied: {job_id}")
    if job.status != EnrichStatus.COMPLETED:
        raise ValueError(f"job not in completed state: {job.status.value}")
    if job.mode not in (EnrichMode.CONFIRM, EnrichMode.AUTO_APPLY):
        raise ValueError(f"job mode does not require apply: {job.mode.value}")
    if job.result is None or not job.result.success:
        raise ValueError(f"job has no successful result to apply: {job_id}")

    applied = _write_concept_metadata(job.concept_path, job.result.metadata)
    if not applied:
        raise RuntimeError(f"metadata write failed: {job.concept_path}")

    job.applied_at = datetime.now(timezone.utc).isoformat()
    _record_metrics_and_audit(
        job=job,
        action="enrich.apply",
        actor=actor,
        var_dir=var_dir,
    )
    return job


def _record_metrics_and_audit(
    *,
    job: EnrichJob,
    action: str,
    actor: str,
    var_dir: Path | None,
) -> None:
    """apply 시 metrics + audit 기록."""
    if var_dir is not None and job.created_at and job.applied_at:
        try:
            created = datetime.fromisoformat(job.created_at.replace("Z", "+00:00"))
            applied = datetime.fromisoformat(job.applied_at.replace("Z", "+00:00"))
            mttr_minutes = (applied - created).total_seconds() / 60.0
            get_metrics_store().record_apply(mttr_minutes=mttr_minutes)
        except (ValueError, TypeError):
            pass

    if var_dir is not None:
        audit.append_audit(
            var_dir,
            action=action,
            actor=actor,
            target_type="concept",
            target_id=job.concept_path,
            details={
                "job_id": job.job_id,
                "confidence": job.result.metadata.confidence if job.result else 0.0,
                "mode": job.mode.value,
            },
        )


__all__ = [
    "create_enrich_job",
    "apply_job",
    "list_jobs",
    "count_jobs",
    "get_job",
    "reset_jobs",
    "AUTO_APPLY_CONFIDENCE_THRESHOLD",
    "is_sdk_available",
]
"""Smoke check #9 (M-v0.0.3-a, 신규): POST /api/v1/enrich dry-run + GET /api/v1/enrich/metrics.

pi-coding-agent SDK 미설치 환경 가정 → result.success=False, error_code=E_NOT_IMPLEMENTED 검증.
metrics endpoint 는 SDK 와 독립적 → 항상 정상 동작 검증.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request


def main() -> int:
    base_url = os.environ.get("AI_LIBRARY_BASE_URL", "http://localhost:8000")

    # 1. bundle 생성 + concept markdown 작성 (var_dir 내부)
    from pathlib import Path
    import uuid
    # backend 의 var_dir 는 backend/var/
    backend_dir = Path(__file__).resolve().parent.parent
    var_dir = backend_dir / "var"
    bundle_name = f"smoke-enrich-{uuid.uuid4().hex[:8]}"
    bundle_dir = var_dir / "bundles" / bundle_name / "concepts" / "adr"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    concept_md = bundle_dir / "test.md"
    concept_md.write_text(
        "# Smoke Concept\n\nBody for smoke test.\n",
        encoding="utf-8",
    )

    try:
        # 2. POST /api/v1/enrich dry-run
        create_url = f"{base_url}/api/v1/enrich"
        body = json.dumps(
            {
                "concept_path": str(concept_md),
                "mode": "dry_run",
            }
        ).encode()
        req = urllib.request.Request(
            create_url,
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as r:
            d = json.loads(r.read())
            assert "job_id" in d["data"]
            assert d["data"]["mode"] == "dry_run"
            # SDK 미설치 환경 → success=False, error_code=E_NOT_IMPLEMENTED
            assert d["data"]["result"]["success"] is False
            assert d["data"]["result"]["error_code"] == "E_NOT_IMPLEMENTED"

        # 3. GET /api/v1/enrich/metrics
        metrics_url = f"{base_url}/api/v1/enrich/metrics"
        with urllib.request.urlopen(urllib.request.Request(metrics_url, method="GET")) as r:
            d = json.loads(r.read())
            assert "mttr_minutes_avg" in d["data"]
            assert "sdk_available" in d["data"]
            assert d["data"]["sdk_available"] is False  # SDK 미설치
    finally:
        # cleanup
        import shutil
        if bundle_dir.parent.parent.parent.exists():
            shutil.rmtree(bundle_dir.parent.parent.parent, ignore_errors=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
"""Smoke check #4 (M-v0.0.2-c): GET /api/v1/search — concept 검색."""
from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request


def main() -> int:
    base_url = os.environ.get("AI_LIBRARY_BASE_URL", "http://localhost:8000")
    # query 가 index 와 substring 매치해야 함 → 흔한 단어로 테스트
    # 실제 검색 동작은 var/bundles/ 에 concept 이 있어야 결과 나옴 (없어도 200 OK)
    url = f"{base_url}/api/v1/search?q=policy&limit=10"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req) as r:
        d = json.loads(r.read())
        # envelope 검증
        assert d["envelope"]["api_version"] == "v1"
        assert "results" in d["data"]
        assert "total" in d["data"]
        assert isinstance(d["data"]["results"], list)
    return 0


if __name__ == "__main__":
    sys.exit(main())
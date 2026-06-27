"""Smoke check #5 (M-v0.0.2-c): GET /api/v1/raw + DELETE /api/v1/raw/{raw_id}."""
from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request


def main() -> int:
    base_url = os.environ.get("AI_LIBRARY_BASE_URL", "http://localhost:8000")

    # 1. mock source sync 로 raw 1개 생성
    sync_url = f"{base_url}/api/v1/ingest/mock/sync?dry_run=false"
    urllib.request.urlopen(urllib.request.Request(sync_url, method="POST")).read()

    # 2. list raw?source=mock
    list_url = f"{base_url}/api/v1/raw?source=mock&limit=5"
    with urllib.request.urlopen(urllib.request.Request(list_url, method="GET")) as r:
        d = json.loads(r.read())
        assert d["data"]["total"] >= 1, f"expected >=1 raw in mock, got {d['data']['total']}"
        raw_id = d["data"]["items"][0]["raw_id"]

    # 3. delete raw
    del_url = f"{base_url}/api/v1/raw/{raw_id}"
    with urllib.request.urlopen(urllib.request.Request(del_url, method="DELETE")) as r:
        d = json.loads(r.read())
        assert d["data"]["deleted"] is True
        assert d["data"]["raw_id"] == raw_id
    return 0


if __name__ == "__main__":
    sys.exit(main())
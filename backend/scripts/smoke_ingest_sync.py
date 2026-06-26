"""Smoke check #5: POST /api/v1/ingest/mock/sync?dry_run=true returns synced=1."""
from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request


def main() -> int:
    base_url = os.environ.get("AI_LIBRARY_BASE_URL", "http://localhost:8000")
    url = f"{base_url}/api/v1/ingest/mock/sync?dry_run=true"
    req = urllib.request.Request(url, method="POST")
    with urllib.request.urlopen(req) as r:
        d = json.loads(r.read())
        assert d["data"]["synced"] == 1, f"expected synced=1, got {d['data']['synced']}"
        assert d["data"]["failed"] == 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
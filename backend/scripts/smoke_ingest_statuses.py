"""Smoke check #4: GET /api/v1/ingest/statuses returns 5 sources."""
from __future__ import annotations

import json
import os
import sys
import urllib.request


def main() -> int:
    base_url = os.environ.get("AI_LIBRARY_BASE_URL", "http://localhost:8000")
    with urllib.request.urlopen(f"{base_url}/api/v1/ingest/statuses") as r:
        d = json.loads(r.read())
        assert d["data"]["total"] == 5, f"expected 5 sources, got {d['data']['total']}"
        sources = [s["source"] for s in d["data"]["sources"]]
        assert "mock" in sources
    return 0


if __name__ == "__main__":
    sys.exit(main())
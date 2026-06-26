"""Smoke check #1: GET /health returns envelope-wrapped data."""
from __future__ import annotations

import json
import os
import sys
import urllib.request


def main() -> int:
    base_url = os.environ.get("AI_LIBRARY_BASE_URL", "http://localhost:8000")
    with urllib.request.urlopen(f"{base_url}/health") as r:
        d = json.loads(r.read())
        assert d["data"]["status"] == "ok", f"status != ok: {d}"
        assert d["envelope"]["api_version"] == "v0-2", f"api_version: {d}"
    return 0


if __name__ == "__main__":
    sys.exit(main())
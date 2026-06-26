"""Smoke check #3: GET /api/v0-2/health/protected with valid Path Y header.

Standalone script (smoke.sh 에서 호출) — quoting 회피.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import urllib.request


def main() -> int:
    base_url = os.environ.get("AI_LIBRARY_BASE_URL", "http://localhost:8000")
    ctx = {
        "version": "v0",
        "user_id": "u_smoke",
        "org_id": "ou_smoke",
        "org_unit_ids": ["ou_smoke"],
        "project_ids": [],
        "roles": ["developer"],
        "request_id": "req_smoke",
        "issued_at": "2026-06-26T00:00:00Z",
    }
    raw = json.dumps(ctx).encode("utf-8")
    encoded = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
    req = urllib.request.Request(
        f"{base_url}/api/v0-2/health/protected",
        headers={"X-AiLibrary-User-Context": encoded},
    )
    with urllib.request.urlopen(req) as r:
        d = json.loads(r.read())
        assert d["envelope"]["path_y_validated"] is True, f"path_y_validated false: {d}"
        assert d["data"]["user_id"] == "u_smoke", f"user_id mismatch: {d}"
    return 0


if __name__ == "__main__":
    sys.exit(main())
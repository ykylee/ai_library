"""Smoke check #6: bundles cycle (create + get + rebuild)."""
from __future__ import annotations

import json
import os
import sys
import urllib.request

BASE_URL = os.environ.get("AI_LIBRARY_BASE_URL", "http://localhost:8000")


def _post(path: str, body: dict) -> dict:
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def _get(path: str) -> dict:
    with urllib.request.urlopen(f"{BASE_URL}{path}") as r:
        return json.loads(r.read())


def main() -> int:
    import uuid
    bundle_name = f"smoke-bundle-{uuid.uuid4().hex[:8]}"

    # 1. create
    create_resp = _post(
        "/api/v1/bundles",
        {
            "name": bundle_name,
            "description": "smoke test bundle",
            "owner_org_id": "ou_smoke",
            "visibility": "org",
        },
    )
    assert create_resp["data"]["name"] == bundle_name, create_resp

    # 2. get
    get_resp = _get(f"/api/v1/bundles/{bundle_name}")
    assert get_resp["data"]["owner_org_id"] == "ou_smoke", get_resp

    # 3. rebuild
    rebuild_resp = _post(
        f"/api/v1/bundles/{bundle_name}/rebuild?dry_run=true", {}
    )
    assert rebuild_resp["data"]["bundle"] == bundle_name, rebuild_resp

    return 0


if __name__ == "__main__":
    sys.exit(main())
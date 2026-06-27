"""Smoke check #6 (M-v0.0.2-c): audit + graph reindex."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid


def main() -> int:
    base_url = os.environ.get("AI_LIBRARY_BASE_URL", "http://localhost:8000")

    # 1. 새 bundle 생성
    bundle_name = f"smoke-graph-reindex-{uuid.uuid4().hex[:8]}"
    create_url = f"{base_url}/api/v1/bundles"
    body = json.dumps({"name": bundle_name, "owner_org_id": "ou_smoke", "visibility": "org"}).encode()
    req = urllib.request.Request(
        create_url, data=body, method="POST", headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req).read()

    # 2. POST /api/v1/graph/reindex?bundle=...&dry_run=false
    reindex_url = f"{base_url}/api/v1/graph/reindex?bundle={bundle_name}&dry_run=false"
    with urllib.request.urlopen(urllib.request.Request(reindex_url, method="POST")) as r:
        d = json.loads(r.read())
        assert d["data"]["bundle"] == bundle_name
        assert d["data"]["dry_run"] is False

    # 3. GET /api/v1/audit?action=graph.reindex
    audit_url = f"{base_url}/api/v1/audit?action=graph.reindex&limit=10"
    with urllib.request.urlopen(urllib.request.Request(audit_url, method="GET")) as r:
        d = json.loads(r.read())
        actions = [e["action"] for e in d["data"]["items"]]
        assert "graph.reindex" in actions
    return 0


if __name__ == "__main__":
    sys.exit(main())
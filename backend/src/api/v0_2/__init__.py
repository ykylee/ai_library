"""ai_library backend — /api/v0-2/ routers.

본 패키지의 6 router (17 endpoint):
- ingest.py   : POST /ingest/{source}/pull + GET /ingest/statuses
- bundles.py  : GET /bundles + GET /bundles/{name} + POST /bundles/{name}/rebuild
- concepts.py : GET /concepts + GET /concepts/{type}/{name}
- raw.py      : GET /raw + DELETE /raw/{id}
- audit.py    : GET /audit
- graph.py    : GET /graph + POST /graph/reindex

M-v0.0.1-alpha = placeholder. 실제 endpoint 는 M-v0.0.2+ 부터 backend core 작성.
"""
from __future__ import annotations

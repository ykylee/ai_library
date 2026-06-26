"""ai_library backend — /api/v0-2/ routers.

본 패키지의 router aggregator:
- health.py   : GET /health (root, via api.root_router) + GET /api/v0-2/health/protected  (M-v0.0.2-a)
- ingest.py   : POST /api/v0-2/ingest/{source}/pull + sync + GET /statuses  (M-v0.0.2-b)
- bundles.py  : GET/POST /api/v0-2/bundles + GET/POST /{name} + /rebuild  (M-v0.0.2-b)
- concepts.py : GET /api/v0-2/search + GET /concepts/{type}/{name}  (M-v0.0.2-c)
- raw.py      : GET /api/v0-2/raw + DELETE /{raw_id}  (M-v0.0.2-c)
- audit.py    : GET /api/v0-2/audit  (M-v0.0.2-c)
- graph.py    : GET /api/v0-2/graph + POST /reindex  (M-v0.0.2-c)

M-v0.0.2-a (foundation) = 본 aggregator + health.py 의 protected_router 만 포함.
M-v0.0.2-b, M-v0.0.2-c 에서 각 router 추가 등록.
"""
from __future__ import annotations

from fastapi import APIRouter

from . import health

# aggregator router (M-v0.0.2-a)
api_v0_2_router = APIRouter(prefix="/api/v0-2")
api_v0_2_router.include_router(health.protected_router)


__all__ = ["api_v0_2_router"]
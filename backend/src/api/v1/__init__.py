"""ai_library backend — /api/v1/ routers.

본 패키지의 router aggregator:
- health.py    : GET /health (root) + GET /api/v1/health/protected  (M-v0.0.2-a)
- ingest.py    : GET /api/v1/ingest/statuses + POST /api/v1/ingest/{source}/sync + /pull  (M-v0.0.2-b)
- bundles.py   : GET/POST /api/v1/bundles + GET /{name} + /rebuild  (M-v0.0.2-b)
- concepts.py  : GET /api/v1/search + GET /concepts/{type}/{name}  (M-v0.0.2-c)
- raw.py       : GET /api/v1/raw + DELETE /{raw_id}  (M-v0.0.2-c)
- audit.py     : GET /api/v1/audit  (M-v0.0.2-c)
- graph.py     : GET /api/v1/graph + POST /reindex  (M-v0.0.2-c)
- monitoring.py: GET /api/v1/monitoring/alerts  (M-v0.0.2-c)

M-v0.0.2-a: 본 aggregator + health.py
M-v0.0.2-b: + ingest.py + bundles.py
M-v0.0.2-c: + concepts.py + raw.py + audit.py + graph.py + monitoring.py
            (총 17 endpoint 등록 완료 = M-v0.0.2 milestone done)
"""
from __future__ import annotations

from fastapi import APIRouter

from . import audit, bundles, concepts, graph, health, ingest, monitoring, raw

# aggregator router (M-v0.0.2-a + b + c)
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(health.protected_router)
api_v1_router.include_router(ingest.router)
api_v1_router.include_router(bundles.router)
api_v1_router.include_router(concepts.router)
api_v1_router.include_router(raw.router)
api_v1_router.include_router(audit.router)
api_v1_router.include_router(graph.router)
api_v1_router.include_router(monitoring.router)


__all__ = ["api_v1_router"]
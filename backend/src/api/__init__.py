"""ai_library backend — /api/ routers (top-level).

`api/` 의 sub-package:
- `envelope.py` : Envelope / EnvelopeMeta / EnvelopeContext
- `errors.py`   : ApiError + register_error_handlers
- `path_y.py`   : Path Y user context (ADR-0001 §2.3 standalone 정책)
- `middleware.py`: HTTP middleware + Depends helpers
- `v0_2/`      : /api/v0-2/ routers (M-v0.0.2+ 부터 6 router 등록, 17 endpoint)
- `v0_3/`      : M-v0.0.6+ 부터 도입 예정 (deprecation policy)

M-v0.0.2-a (foundation) = envelope + errors + path_y + middleware + v0_2/health
"""
from __future__ import annotations

from fastapi import FastAPI

from .errors import register_error_handlers
from .middleware import attach_envelope_middleware
from .v0_2.health import root_router as health_root_router


def install_middleware(app: FastAPI) -> None:
    """FastAPI app 에 envelope middleware + error handler 등록.

    호출 시점 = `create_app()` 내부, router 등록 전.
    """
    app.middleware("http")(attach_envelope_middleware)
    register_error_handlers(app)


def install_root_routers(app: FastAPI) -> None:
    """Root-level router 등록 (prefix 없는 endpoint).

    M-v0.0.2-a: health (GET /health).
    """
    app.include_router(health_root_router)


__all__ = ["install_middleware", "install_root_routers"]
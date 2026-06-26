"""HTTP middleware (envelope context 주입).

request 들어올 때:
1. request.state.envelope = EnvelopeContext.new(path_y=...)
2. request.state.path_y = PathYUserContext | None

endpoint 는 FastAPI `Depends(get_envelope)` 로 envelope context 수신.
"""
from __future__ import annotations

from fastapi import Request

from .envelope import EnvelopeContext
from .path_y import PathYUserContext, parse_path_y


HEADER_PATH_Y = "X-AiLibrary-User-Context"


async def attach_envelope_middleware(request: Request, call_next):
    """FastAPI middleware: parse Path Y + create EnvelopeContext per request.

    ASGI middleware 방식 대신 Starlette `BaseHTTPMiddleware` subclass 보다
    dependency 방식이 더 명시적. 본 함수는 미사용 (남겨둔 이유는 향후 trace_id
    propagation 등 추가 middleware 확장 시 reference).
    """
    path_y_header = request.headers.get(HEADER_PATH_Y)
    path_y = parse_path_y(path_y_header)
    request.state.path_y = path_y
    request.state.envelope = EnvelopeContext.new(path_y=path_y)
    response = await call_next(request)
    return response


def get_envelope(request: Request) -> EnvelopeContext:
    """FastAPI dependency: endpoint 에서 EnvelopeContext 수신."""
    if not hasattr(request.state, "envelope"):
        # middleware 미적용 시 fallback (test / direct call)
        request.state.envelope = EnvelopeContext.new(
            path_y=parse_path_y(request.headers.get(HEADER_PATH_Y))
        )
    return request.state.envelope


def get_path_y(request: Request) -> PathYUserContext | None:
    """FastAPI dependency: Path Y context 수신 (optional, None 가능)."""
    return getattr(request.state, "path_y", None)


__all__ = ["attach_envelope_middleware", "get_envelope", "get_path_y", "HEADER_PATH_Y"]
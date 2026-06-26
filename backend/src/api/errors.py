"""API error 정의 + global exception handler.

web frontend `ApiErrorBody` = `{ detail: { code, message } }` 형식 정합.

사용 패턴:
    raise ApiError(status=404, code="E_NOT_FOUND", message="concept not found")

middleware 가 FastAPI exception_handler 로 등록되어 JSONResponse 변환.
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ApiError(Exception):
    """API error (status + code + message).

    web frontend 의 `ApiError` 와 semantic 정합. code 는 machine-readable 영문 enum
    (예: `E_NOT_FOUND`, `E_BAD_REQUEST`, `E_INTERNAL`, `E_UNAUTHORIZED`).
    """

    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


async def api_error_handler(_request: Request, exc: ApiError) -> JSONResponse:
    """Global ApiError handler → JSONResponse with `{detail: {code, message}}`."""
    return JSONResponse(
        status_code=exc.status,
        content={"detail": {"code": exc.code, "message": exc.message}},
    )


def register_error_handlers(app: FastAPI) -> None:
    """FastAPI app 에 ApiError handler 등록."""
    app.add_exception_handler(ApiError, api_error_handler)


__all__ = ["ApiError", "register_error_handlers"]
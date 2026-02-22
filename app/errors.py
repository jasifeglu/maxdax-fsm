"""Global API error handling utilities."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException


class ApiError(Exception):
    """Domain-level API exception."""

    def __init__(self, code: str, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def install_error_handlers(app: FastAPI) -> None:
    """Register consistent JSON error handlers."""

    @app.exception_handler(ApiError)
    async def api_error_handler(_: Request, exc: ApiError) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": "http_error", "message": exc.detail}},
        )

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(_: Request, exc: ValidationError) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": {"code": "validation_error", "message": "Request validation failed", "details": exc.errors()}},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, __: Exception) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": {"code": "internal_server_error", "message": "An unexpected error occurred"}},
        )

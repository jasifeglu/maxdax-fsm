"""Production-focused API entrypoint."""

from __future__ import annotations

import hashlib
from typing import Annotated

from fastapi import FastAPI, Query
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, Field

from app.cache import AppCache, benchmark
from app.config import get_settings
from app.errors import ApiError, install_error_handlers
from app.security import configure_security


class ScoreRequest(BaseModel):
    """Validated API request payload."""

    name: str = Field(min_length=2, max_length=100)
    values: list[float] = Field(min_length=1, max_length=10_000)


class ScoreResponse(BaseModel):
    """Response payload for score endpoint."""

    id: str
    total: float
    average: float
    count: int
    compute_time_ms: float


def create_app() -> FastAPI:
    """Application factory for server and tests."""

    settings = get_settings()
    app = FastAPI(title=settings.app_name, default_response_class=ORJSONResponse, debug=settings.debug)

    cache = AppCache(maxsize=settings.cache_max_entries, ttl=settings.cache_ttl_seconds)

    configure_security(app, settings.allowed_origins)
    install_error_handlers(app)

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment}

    @app.get("/metrics/cache")
    async def cache_metrics() -> dict[str, float]:
        return cache.stats()

    @app.post("/v1/score", response_model=ScoreResponse)
    async def score(payload: ScoreRequest, _: Annotated[str | None, Query(alias="request_id")] = None) -> ScoreResponse:
        if len(payload.values) > 100_000:
            raise ApiError("payload_too_large", "Too many values provided", 413)

        payload_hash = hashlib.sha256(payload.model_dump_json().encode("utf-8")).hexdigest()
        cache_key = f"score:{payload_hash}"

        def compute() -> ScoreResponse:
            total = sum(payload.values)
            count = len(payload.values)
            avg = total / count
            return ScoreResponse(id=payload_hash[:12], total=total, average=avg, count=count, compute_time_ms=0.0)

        result, duration_ms = benchmark(lambda: cache.get_or_compute(cache_key, compute))
        result.compute_time_ms = duration_ms
        return result

    return app


app = create_app()

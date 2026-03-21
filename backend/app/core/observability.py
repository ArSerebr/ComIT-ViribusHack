"""Health/readiness, request logging, request_id + единый JSON для ошибок."""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.db.session import get_db
from app.core.redis_client import get_redis

logger = logging.getLogger("viribus.request")

health_router = APIRouter(tags=["health"])


@health_router.get("/health")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@health_router.get("/ready")
async def readiness(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    await db.execute(text("SELECT 1"))
    await get_redis().ping()
    return {"status": "ok"}


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = rid
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            "request_id=%s method=%s path=%s status=%s duration_ms=%s",
            rid,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        response.headers["X-Request-ID"] = rid
        return response


def _with_request_id(request: Request, body: dict[str, Any]) -> dict[str, Any]:
    rid = getattr(request.state, "request_id", None)
    if rid:
        out = dict(body)
        out["request_id"] = rid
        return out
    return body


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    rid = getattr(request.state, "request_id", None)
    detail = exc.detail
    if isinstance(detail, str):
        body: dict[str, Any] = {"detail": detail}
    elif isinstance(detail, dict):
        body = dict(detail)
    else:
        body = {"detail": detail}
    body = _with_request_id(request, body)
    headers = {"X-Request-ID": rid} if rid else {}
    return JSONResponse(status_code=exc.status_code, content=body, headers=headers)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    rid = getattr(request.state, "request_id", None)
    body: dict[str, Any] = {"detail": exc.errors()}
    body = _with_request_id(request, body)
    headers = {"X-Request-ID": rid} if rid else {}
    return JSONResponse(status_code=422, content=body, headers=headers)


def register_observability(app: FastAPI) -> None:
    app.include_router(health_router)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_middleware(RequestContextMiddleware)

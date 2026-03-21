from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from app.core.db.session import engine
from app.core.redis_client import close_redis
from app.openapi_export import export_openapi_yaml
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    export_openapi_yaml(app)
    yield
    await engine.dispose()
    await close_redis()

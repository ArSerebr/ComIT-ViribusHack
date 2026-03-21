from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.core.db.session import engine
from app.core.redis_client import close_redis
from app.openapi_export import export_openapi_yaml


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    export_openapi_yaml(app)
    yield
    await engine.dispose()
    await close_redis()

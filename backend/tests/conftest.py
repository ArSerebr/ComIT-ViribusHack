"""Общая конфигурация pytest: переменные окружения до импорта приложения."""

from __future__ import annotations

import os

# Settings и engine читают окружение при импорте модулей приложения.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/viribus",
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-for-pytest")

# Сессии Bearer (RedisStrategy): подмена на fakeredis, чтобы pytest не требовал живой Redis
# и реально выполнял команды GET/SET/DEL как в проде.
import app.core.redis_client as _redis_client_module
from fakeredis import FakeAsyncRedis

_redis_client_module.redis_client = FakeAsyncRedis(decode_responses=True)

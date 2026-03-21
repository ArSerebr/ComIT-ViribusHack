"""Проверка хранения сессионных токенов в Redis (через RedisStrategy / fakeredis в conftest)."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from fastapi_users.authentication.strategy.redis import RedisStrategy

from app.config import get_settings
from app.core.redis_client import get_redis
from app.modules.auth.jwt_backend import auth_backend, get_redis_strategy


def test_auth_backend_wires_redis_strategy():
    strat = get_redis_strategy()
    assert isinstance(strat, RedisStrategy)
    assert strat.lifetime_seconds == get_settings().jwt_lifetime_seconds
    assert auth_backend.name == "jwt"


@pytest.mark.asyncio
async def test_redis_strategy_stores_user_id_and_resolves_user():
    redis = get_redis()
    strat = RedisStrategy(
        redis=redis,
        lifetime_seconds=get_settings().jwt_lifetime_seconds,
    )
    uid = uuid4()
    user = MagicMock()
    user.id = uid

    token = await strat.write_token(user)
    assert token
    key = f"fastapi_users_token:{token}"
    assert await redis.get(key) == str(uid)

    user_manager = AsyncMock()
    user_manager.parse_id = lambda raw: UUID(raw) if isinstance(raw, str) else raw
    user_manager.get = AsyncMock(return_value=user)

    loaded = await strat.read_token(token, user_manager)
    assert loaded is user
    user_manager.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_redis_strategy_destroy_token_removes_key():
    redis = get_redis()
    strat = RedisStrategy(redis=redis, lifetime_seconds=60)
    uid = uuid4()
    user = MagicMock()
    user.id = uid

    token = await strat.write_token(user)
    key = f"fastapi_users_token:{token}"
    assert await redis.get(key) == str(uid)

    await strat.destroy_token(token, user)
    assert await redis.get(key) is None


@pytest.mark.asyncio
async def test_redis_strategy_unknown_token_returns_none():
    strat = RedisStrategy(redis=get_redis(), lifetime_seconds=60)
    user_manager = AsyncMock()
    assert await strat.read_token("not-a-valid-session", user_manager) is None
    user_manager.get.assert_not_awaited()

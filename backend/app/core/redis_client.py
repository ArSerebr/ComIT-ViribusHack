from __future__ import annotations

import redis.asyncio as redis_async
from app.config import get_settings

_settings = get_settings()

redis_client = redis_async.from_url(
    _settings.redis_url,
    decode_responses=True,
)


def get_redis() -> redis_async.Redis:
    """Общий async-клиент Redis для auth (RedisStrategy) и др."""
    return redis_client


async def close_redis() -> None:
    await redis_client.aclose()

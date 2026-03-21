"""Bearer transport + Redis-backed session tokens для fastapi-users (opaque access_token)."""
from __future__ import annotations

from fastapi_users.authentication import AuthenticationBackend, BearerTransport, RedisStrategy

from app.config import get_settings
from app.core.redis_client import get_redis

_settings = get_settings()

bearer_transport = BearerTransport(tokenUrl="/api/auth/jwt/login")


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(
        redis=get_redis(),
        lifetime_seconds=_settings.jwt_lifetime_seconds,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_redis_strategy,
)

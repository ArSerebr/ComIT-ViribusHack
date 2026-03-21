"""JWT transport + backend для fastapi-users."""
from __future__ import annotations

from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy

from app.config import get_settings

_settings = get_settings()

bearer_transport = BearerTransport(tokenUrl="/api/auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=_settings.jwt_secret,
        lifetime_seconds=_settings.jwt_lifetime_seconds,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

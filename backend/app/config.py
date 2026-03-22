from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Один общий `.env` в корне репозитория (рядом с docker-compose.yml).
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Настройки из переменных окружения и из корневого `.env`."""

    model_config = SettingsConfigDict(
        env_file=str(_REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Только из окружения / корневого `.env` (переменная DATABASE_URL).
    database_url: str
    sqlalchemy_echo: bool = False

    # Redis (сессии Bearer через RedisStrategy в fastapi-users; в Docker — хост `redis`).
    redis_url: str = "redis://localhost:6379/0"

    # QmsgCore (групповой чат); в Docker — http://qmsg-core:8090, локально — http://localhost:8090.
    qmsg_core_base_url: str = "http://localhost:8090"

    # JWT и токены сброса/верификации пароля (fastapi-users).
    jwt_secret: str = Field(
        ...,
        description="Секрет подписи access JWT и по умолчанию — reset/verify токенов.",
    )
    jwt_lifetime_seconds: int = 3600
    reset_password_token_secret: str | None = None
    verification_token_secret: str | None = None

    @model_validator(mode="after")
    def default_token_secrets_from_jwt(self) -> Self:
        if not self.reset_password_token_secret:
            self.reset_password_token_secret = self.jwt_secret
        if not self.verification_token_secret:
            self.verification_token_secret = self.jwt_secret
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()

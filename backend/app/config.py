from __future__ import annotations

from functools import lru_cache
from pathlib import Path

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


@lru_cache
def get_settings() -> Settings:
    return Settings()

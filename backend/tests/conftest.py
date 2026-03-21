"""Общая конфигурация pytest: переменные окружения до импорта приложения."""
from __future__ import annotations

import os

# Settings и engine читают окружение при импорте модулей приложения.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/viribus",
)
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-for-pytest")

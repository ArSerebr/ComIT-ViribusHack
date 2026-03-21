"""Pydantic-схемы пользователя для fastapi-users."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.modules.auth.models import UserRole
from fastapi_users import schemas


class UserRead(schemas.BaseUser[UUID]):
    role: UserRole


class UserCreate(schemas.BaseUserCreate):
    """Регистрация: роль с клиента не задаётся (только email/password + safe create)."""


class UserUpdate(schemas.BaseUserUpdate):
    role: UserRole | None = None

    def create_update_dict(self) -> dict[str, Any]:
        return schemas.model_dump(
            self,
            exclude_unset=True,
            exclude={
                "id",
                "is_superuser",
                "is_active",
                "is_verified",
                "oauth_accounts",
                "role",
            },
        )

    def create_update_dict_superuser(self) -> dict[str, Any]:
        return schemas.model_dump(self, exclude_unset=True, exclude={"id"})

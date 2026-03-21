"""Pydantic-схемы пользователя для fastapi-users."""
from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from fastapi_users import schemas

from app.modules.auth.models import UserRole


class UserRead(schemas.BaseUser[UUID]):
    role: UserRole


class UserCreate(schemas.BaseUserCreate):
    """Регистрация: роль с клиента не задаётся (только email/password + safe create)."""


class UserUpdate(schemas.BaseUserUpdate):
    role: Optional[UserRole] = None

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

"""UserManager: пароли, синхронизация role ↔ is_superuser."""

from __future__ import annotations

import uuid
from typing import Any

from app.config import get_settings
from app.modules.auth.models import User, UserRole
from fastapi import Request
from fastapi_users import BaseUserManager, UUIDIDMixin

_settings = get_settings()


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = _settings.reset_password_token_secret  # type: ignore[assignment]
    verification_token_secret = _settings.verification_token_secret  # type: ignore[assignment]

    async def on_after_register(self, user: User, request: Request | None = None) -> None:
        await self._sync_role_superuser(user)

    async def on_after_update(
        self,
        user: User,
        update_dict: dict[str, Any],
        request: Request | None = None,
    ) -> None:
        await self._sync_role_superuser(user)

    async def _sync_role_superuser(self, user: User) -> None:
        """Согласовать `admin` ↔ `is_superuser`; исправить противоречия."""
        role_val = user.role
        role_str = role_val.value if isinstance(role_val, UserRole) else str(role_val)

        updates: dict[str, Any] = {}
        if user.is_superuser and role_str != UserRole.admin.value:
            updates["role"] = UserRole.admin.value
        elif role_str == UserRole.admin.value and not user.is_superuser:
            updates["is_superuser"] = True
        elif role_str != UserRole.admin.value and user.is_superuser:
            updates["is_superuser"] = False

        if updates:
            await self.user_db.update(user, updates)

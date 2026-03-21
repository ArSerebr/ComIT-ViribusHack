"""Согласование role ↔ is_superuser в UserManager._sync_role_superuser."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.auth.manager import UserManager
from app.modules.auth.models import UserRole


@pytest.mark.asyncio
async def test_sync_superuser_non_admin_role_sets_admin_role():
    user_db = AsyncMock()
    manager = UserManager(user_db)
    user = MagicMock()
    user.role = UserRole.user
    user.is_superuser = True

    await manager._sync_role_superuser(user)

    user_db.update.assert_awaited_once_with(user, {"role": UserRole.admin.value})


@pytest.mark.asyncio
async def test_sync_admin_role_without_superuser_sets_superuser():
    user_db = AsyncMock()
    manager = UserManager(user_db)
    user = MagicMock()
    user.role = UserRole.admin
    user.is_superuser = False

    await manager._sync_role_superuser(user)

    user_db.update.assert_awaited_once_with(user, {"is_superuser": True})


@pytest.mark.asyncio
async def test_sync_moderator_with_superuser_promotes_role_to_admin():
    """При is_superuser и роли не admin роль приводится к admin (ветка 1)."""
    user_db = AsyncMock()
    manager = UserManager(user_db)
    user = MagicMock()
    user.role = UserRole.moderator
    user.is_superuser = True

    await manager._sync_role_superuser(user)

    user_db.update.assert_awaited_once_with(user, {"role": UserRole.admin.value})


@pytest.mark.asyncio
async def test_sync_no_update_when_already_consistent():
    user_db = AsyncMock()
    manager = UserManager(user_db)
    user = MagicMock()
    user.role = UserRole.admin
    user.is_superuser = True

    await manager._sync_role_superuser(user)

    user_db.update.assert_not_awaited()

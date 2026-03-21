"""NotificationsService: список уведомлений по user_id."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest
from app.modules.notifications.service import NotificationsService


@pytest.mark.asyncio
async def test_list_notifications_delegates_to_repo():
    repo = AsyncMock()
    repo.list_ordered_for_user = AsyncMock(return_value=[])
    uid = uuid.uuid4()
    svc = NotificationsService(repo)

    out = await svc.list_notifications(uid)

    assert out == []
    repo.list_ordered_for_user.assert_awaited_once_with(uid)

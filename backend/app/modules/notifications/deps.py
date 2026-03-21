from __future__ import annotations

from app.core.db.session import get_db
from app.modules.notifications.repository import NotificationsRepository
from app.modules.notifications.service import NotificationsService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_notifications_service(
    session: AsyncSession = Depends(get_db),
) -> NotificationsService:
    return NotificationsService(NotificationsRepository(session))

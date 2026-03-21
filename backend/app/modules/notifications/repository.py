from __future__ import annotations

import uuid

from app.modules.notifications.models import NotificationsItem
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class NotificationsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_ordered_for_user(self, user_id: uuid.UUID) -> list[NotificationsItem]:
        stmt = (
            select(NotificationsItem)
            .where(NotificationsItem.user_id == user_id)
            .order_by(
                NotificationsItem.sort_order,
                NotificationsItem.id,
            )
        )
        return list((await self._session.execute(stmt)).scalars().all())

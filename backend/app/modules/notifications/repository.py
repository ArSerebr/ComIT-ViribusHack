from __future__ import annotations

from app.modules.notifications.models import NotificationsItem
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class NotificationsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_ordered(self) -> list[NotificationsItem]:
        stmt = select(NotificationsItem).order_by(
            NotificationsItem.sort_order,
            NotificationsItem.id,
        )
        return list((await self._session.execute(stmt)).scalars().all())

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.it_news.models import ItNewsItem


class ItNewsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_recent(
        self,
        *,
        source: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ItNewsItem]:
        q = select(ItNewsItem).order_by(
            ItNewsItem.published_at.desc().nullslast(),
            ItNewsItem.created_at.desc(),
        )
        if source:
            q = q.where(ItNewsItem.source == source)
        q = q.limit(limit).offset(offset)
        r = await self._session.execute(q)
        return list(r.scalars().all())

    async def get_by_id(self, item_id: uuid.UUID) -> ItNewsItem | None:
        r = await self._session.execute(select(ItNewsItem).where(ItNewsItem.id == item_id))
        return r.scalar_one_or_none()

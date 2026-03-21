from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.news.models import NewsFeatured, NewsMini


class NewsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_mini_ordered(self) -> list[NewsMini]:
        stmt = select(NewsMini).order_by(NewsMini.sort_order, NewsMini.id)
        return list((await self._session.execute(stmt)).scalars().all())

    async def list_featured_ordered(self) -> list[NewsFeatured]:
        stmt = select(NewsFeatured).order_by(NewsFeatured.sort_order, NewsFeatured.id)
        return list((await self._session.execute(stmt)).scalars().all())

from __future__ import annotations

from app.modules.news.models import NewsFeatured, NewsMini
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession


class NewsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_mini_ordered(self) -> list[NewsMini]:
        stmt = select(NewsMini).order_by(NewsMini.sort_order, NewsMini.id)
        return list((await self._session.execute(stmt)).scalars().all())

    async def list_featured_ordered(self) -> list[NewsFeatured]:
        stmt = select(NewsFeatured).order_by(NewsFeatured.sort_order, NewsFeatured.id)
        return list((await self._session.execute(stmt)).scalars().all())

    async def get_mini(self, news_id: str) -> NewsMini | None:
        stmt = select(NewsMini).where(NewsMini.id == news_id)
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def add_mini(self, row: NewsMini) -> None:
        self._session.add(row)

    async def delete_mini(self, news_id: str) -> bool:
        res = await self._session.execute(delete(NewsMini).where(NewsMini.id == news_id))
        return (res.rowcount or 0) > 0

    async def max_mini_sort_order(self) -> int:
        stmt = select(func.coalesce(func.max(NewsMini.sort_order), -1))
        v = (await self._session.execute(stmt)).scalar_one()
        return int(v) if v is not None else -1

    async def get_featured(self, news_id: str) -> NewsFeatured | None:
        stmt = select(NewsFeatured).where(NewsFeatured.id == news_id)
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def add_featured(self, row: NewsFeatured) -> None:
        self._session.add(row)

    async def delete_featured(self, news_id: str) -> bool:
        res = await self._session.execute(delete(NewsFeatured).where(NewsFeatured.id == news_id))
        return (res.rowcount or 0) > 0

    async def max_featured_sort_order(self) -> int:
        stmt = select(func.coalesce(func.max(NewsFeatured.sort_order), -1))
        v = (await self._session.execute(stmt)).scalar_one()
        return int(v) if v is not None else -1

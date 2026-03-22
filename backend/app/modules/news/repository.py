from __future__ import annotations

import uuid
from collections.abc import Sequence

from app.modules.news.models import NewsFeatured, NewsFeaturedParticipant, NewsMini
from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
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

    async def get_mini_by_ids(self, ids: Sequence[str]) -> list[NewsMini]:
        if not ids:
            return []
        stmt = select(NewsMini).where(NewsMini.id.in_(ids))
        return list((await self._session.execute(stmt)).scalars().unique().all())

    async def add_mini(self, row: NewsMini) -> None:
        self._session.add(row)

    async def commit(self) -> None:
        await self._session.commit()

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

    async def get_featured_by_ids(self, ids: Sequence[str]) -> list[NewsFeatured]:
        if not ids:
            return []
        stmt = select(NewsFeatured).where(NewsFeatured.id.in_(ids))
        return list((await self._session.execute(stmt)).scalars().unique().all())

    async def add_featured(self, row: NewsFeatured) -> None:
        self._session.add(row)

    async def delete_featured(self, news_id: str) -> bool:
        res = await self._session.execute(delete(NewsFeatured).where(NewsFeatured.id == news_id))
        return (res.rowcount or 0) > 0

    async def max_featured_sort_order(self) -> int:
        stmt = select(func.coalesce(func.max(NewsFeatured.sort_order), -1))
        v = (await self._session.execute(stmt)).scalar_one()
        return int(v) if v is not None else -1

    async def add_participant(self, user_id: uuid.UUID, featured_id: str) -> None:
        stmt = insert(NewsFeaturedParticipant).values(
            user_id=user_id,
            featured_id=featured_id,
        ).on_conflict_do_nothing(index_elements=["user_id", "featured_id"])
        await self._session.execute(stmt)

    async def get_participant_ids(self, user_id: uuid.UUID) -> list[str]:
        stmt = select(NewsFeaturedParticipant.featured_id).where(
            NewsFeaturedParticipant.user_id == user_id
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return list(rows)

    async def count_participants_by_user_ids(
        self, user_ids: Sequence[uuid.UUID]
    ) -> int:
        """Count participation rows where user_id is in user_ids."""
        if not user_ids:
            return 0
        stmt = (
            select(func.count())
            .select_from(NewsFeaturedParticipant)
            .where(NewsFeaturedParticipant.user_id.in_(user_ids))
        )
        return int((await self._session.execute(stmt)).scalar_one() or 0)

    async def list_participations_for_export(
        self, user_ids: Sequence[uuid.UUID]
    ) -> list[tuple[uuid.UUID, str, str]]:
        """Return (user_id, featured_id, event_title) for participations of given users."""
        if not user_ids:
            return []
        stmt = (
            select(
                NewsFeaturedParticipant.user_id,
                NewsFeaturedParticipant.featured_id,
                NewsFeatured.title,
            )
            .join(
                NewsFeatured,
                NewsFeatured.id == NewsFeaturedParticipant.featured_id,
            )
            .where(NewsFeaturedParticipant.user_id.in_(user_ids))
            .order_by(NewsFeaturedParticipant.user_id, NewsFeaturedParticipant.featured_id)
        )
        rows = (await self._session.execute(stmt)).all()
        return [(r[0], r[1], r[2]) for r in rows]

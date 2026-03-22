"""Сохранение IT-новостей."""

from __future__ import annotations

import uuid

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ItNewsItem
from app.news.models_dataclass import RawItNews


async def upsert_it_news(session: AsyncSession, items: list[RawItNews]) -> int:
    count = 0
    for raw in items:
        stmt = insert(ItNewsItem).values(
            id=uuid.uuid4(),
            external_id=raw.external_id,
            source=raw.source,
            title=raw.title,
            summary=raw.summary,
            url=raw.url,
            published_at=raw.published_at,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["source", "external_id"],
            set_=dict(
                title=raw.title,
                summary=raw.summary,
                url=raw.url,
                published_at=raw.published_at,
                updated_at=func.now(),
            ),
        )
        await session.execute(stmt)
        count += 1
    if count > 0:
        await session.commit()
    return count

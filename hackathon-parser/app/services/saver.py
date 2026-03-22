"""Сохранение спарсенных хакатонов в БД."""

from __future__ import annotations

import uuid

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Hackathon
from app.parsers.base import RawHackathon


async def upsert_hackathons(session: AsyncSession, items: list[RawHackathon]) -> int:
    """Insert или update хакатонов. Возвращает количество обработанных."""
    count = 0
    for raw in items:
        stmt = insert(Hackathon).values(
            id=uuid.uuid4(),
            external_id=raw.external_id,
            source=raw.source,
            title=raw.title,
            description=raw.description,
            description_raw=raw.description_raw,
            start_date=raw.start_date,
            end_date=raw.end_date,
            registration_deadline=raw.registration_deadline,
            location=raw.location,
            is_online=raw.is_online,
            prize_pool=raw.prize_pool,
            url=raw.url,
            image_url=raw.image_url,
            organizer=raw.organizer,
            tags=raw.tags,
            status=raw.status,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["source", "external_id"],
            set_=dict(
                title=raw.title,
                description=raw.description,
                description_raw=raw.description_raw,
                start_date=raw.start_date,
                end_date=raw.end_date,
                registration_deadline=raw.registration_deadline,
                location=raw.location,
                is_online=raw.is_online,
                prize_pool=raw.prize_pool,
                url=raw.url,
                image_url=raw.image_url,
                organizer=raw.organizer,
                tags=raw.tags,
                status=raw.status,
                updated_at=func.now(),
            ),
        )
        await session.execute(stmt)
        count += 1
    if count > 0:
        await session.commit()
    return count

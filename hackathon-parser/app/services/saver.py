"""Сохранение спарсенных хакатонов в БД с дедупликацией."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Hackathon
from app.parsers.base import RawHackathon
from app.services.dedup import compute_dedup_key


def _merge_source_urls(existing: list | None, source: str, url: str | None) -> list:
    """Добавить source+url в список, если ещё нет."""
    urls = list(existing or [])
    if not url:
        return urls
    if any(s.get("source") == source and s.get("url") == url for s in urls):
        return urls
    urls.append({"source": source, "url": url})
    return urls


async def upsert_hackathons(session: AsyncSession, items: list[RawHackathon]) -> int:
    """Insert или update хакатонов. Объединяет дубликаты из разных источников."""
    count = 0
    for raw in items:
        dedup_key = compute_dedup_key(raw.title, raw.start_date)
        result = await session.execute(select(Hackathon).where(Hackathon.dedup_key == dedup_key))
        existing = result.scalar_one_or_none()

        if existing:
            if existing.source != raw.source:
                # Тот же хакатон с другого источника — мержим в существующую запись
                existing.source_urls = _merge_source_urls(
                    existing.source_urls, raw.source, raw.url
                )
                if raw.description and (
                    not existing.description
                    or len(raw.description or "") > len(existing.description or "")
                ):
                    existing.description = raw.description
                if raw.prize_pool and not existing.prize_pool:
                    existing.prize_pool = raw.prize_pool
                if raw.tags and not existing.tags:
                    existing.tags = raw.tags
            else:
                # Тот же источник — обновляем данные (повторный парсинг)
                existing.title = raw.title
                existing.description = raw.description
                existing.description_raw = raw.description_raw
                existing.start_date = raw.start_date
                existing.end_date = raw.end_date
                existing.location = raw.location
                existing.is_online = raw.is_online
                existing.prize_pool = raw.prize_pool
                existing.url = raw.url
                existing.image_url = raw.image_url
                existing.organizer = raw.organizer
                existing.tags = raw.tags
                existing.status = raw.status
            existing.updated_at = func.now()
            count += 1
            continue

        source_urls = [{"source": raw.source, "url": raw.url}] if raw.url else []
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
            dedup_key=dedup_key,
            source_urls=source_urls,
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
                dedup_key=dedup_key,
                updated_at=func.now(),
            ),
        )
        await session.execute(stmt)
        count += 1

    if count > 0:
        await session.commit()
    return count

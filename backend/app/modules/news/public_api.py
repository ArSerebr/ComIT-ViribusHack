"""News public API for cross-module consumption (no ORM leakage)."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from app.modules.news.repository import NewsRepository
from schemas import RecommendationCard
from sqlalchemy.ext.asyncio import AsyncSession


async def get_mini_cards_by_ids(
    session: AsyncSession, ids: Sequence[str]
) -> list[RecommendationCard]:
    """Return RecommendationCards for news_mini by ids (subtitle empty)."""
    repo = NewsRepository(session)
    rows = await repo.get_mini_by_ids(list(ids))
    return [
        RecommendationCard(
            id=r.id,
            title=r.title,
            subtitle="",
            image=r.image_url,
            link=r.details_url,
        )
        for r in rows
    ]


async def get_featured_cards_by_ids(
    session: AsyncSession, ids: Sequence[str]
) -> list[RecommendationCard]:
    """Return RecommendationCards for news_featured by ids."""
    repo = NewsRepository(session)
    rows = await repo.get_featured_by_ids(list(ids))
    return [
        RecommendationCard(
            id=r.id,
            title=r.title,
            subtitle=r.subtitle,
            image=r.image_url,
            link=r.details_url,
        )
        for r in rows
    ]


async def count_participants_by_user_ids(
    session: AsyncSession, user_ids: Sequence[uuid.UUID]
) -> int:
    """Count participation rows where user_id is in user_ids."""
    repo = NewsRepository(session)
    return await repo.count_participants_by_user_ids(user_ids)


async def list_participations_for_export(
    session: AsyncSession, user_ids: Sequence[uuid.UUID]
) -> list[tuple[uuid.UUID, str, str]]:
    """Return (user_id, featured_id, event_title) for participations of given users."""
    repo = NewsRepository(session)
    return await repo.list_participations_for_export(user_ids)

"""Публичный API модуля recommendations для других bounded context."""

from __future__ import annotations

from collections.abc import Sequence

from app.modules.recommendations.repository import RecommendationCatalogRepository
from schemas import RecommendationCard
from sqlalchemy.ext.asyncio import AsyncSession


async def get_catalog_cards_by_ids(
    session: AsyncSession, ids: Sequence[str]
) -> list[RecommendationCard]:
    """Вернуть RecommendationCard для строк recommendation_catalog."""
    repo = RecommendationCatalogRepository(session)
    rows = await repo.get_by_ids(list(ids))
    return [
        RecommendationCard(
            id=r.id,
            title=r.title,
            subtitle=r.subtitle,
            image=r.image_url,
            link=r.link_url,
        )
        for r in rows
    ]

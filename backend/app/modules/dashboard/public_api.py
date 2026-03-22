"""Dashboard public API for cross-module consumption (no ORM leakage)."""

from __future__ import annotations

from collections.abc import Sequence

from app.modules.dashboard.repository import DashboardRepository
from schemas import RecommendationCard
from sqlalchemy.ext.asyncio import AsyncSession


async def get_recommendation_cards_by_ids(
    session: AsyncSession, ids: Sequence[str]
) -> list[RecommendationCard]:
    """Return RecommendationCards for dashboard_recommendation by ids."""
    repo = DashboardRepository(session)
    rows = await repo.get_recommendations_by_ids(list(ids))
    return [
        RecommendationCard(
            id=r.id,
            title=r.title,
            subtitle=r.subtitle,
            image=r.image,
            link=r.link,
        )
        for r in rows
    ]


async def list_recommendation_cards_ordered(
    session: AsyncSession,
) -> list[RecommendationCard]:
    """Return all dashboard recommendations in sort order (static fallback)."""
    repo = DashboardRepository(session)
    rows = await repo.list_recommendations_ordered()
    return [
        RecommendationCard(
            id=r.id,
            title=r.title,
            subtitle=r.subtitle,
            image=r.image,
            link=r.link,
        )
        for r in rows
    ]

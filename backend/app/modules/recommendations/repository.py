"""Репозиторий каталога рекомендаций."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.recommendations.models import RecommendationCatalogItem


class RecommendationCatalogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_ids(self, ids: list[str]) -> list[RecommendationCatalogItem]:
        if not ids:
            return []
        result = await self._session.execute(
            select(RecommendationCatalogItem).where(
                RecommendationCatalogItem.id.in_(ids),
                RecommendationCatalogItem.is_active.is_(True),
            )
        )
        rows = list(result.scalars().all())
        by_id = {r.id: r for r in rows}
        return [by_id[i] for i in ids if i in by_id]

    async def list_active_ordered(self) -> list[RecommendationCatalogItem]:
        result = await self._session.execute(
            select(RecommendationCatalogItem)
            .where(RecommendationCatalogItem.is_active.is_(True))
            .order_by(
                RecommendationCatalogItem.sort_order.asc(),
                RecommendationCatalogItem.id.asc(),
            )
        )
        return list(result.scalars().all())

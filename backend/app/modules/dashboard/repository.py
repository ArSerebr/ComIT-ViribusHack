from __future__ import annotations

from collections.abc import Sequence

from app.modules.dashboard.models import DashboardHomeSnapshot, DashboardRecommendation
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class DashboardRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @property
    def session(self) -> AsyncSession:
        return self._session

    async def list_recommendations_ordered(self) -> list[DashboardRecommendation]:
        stmt = select(DashboardRecommendation).order_by(
            DashboardRecommendation.sort_order,
            DashboardRecommendation.id,
        )
        return list((await self._session.execute(stmt)).scalars().all())

    async def get_recommendations_by_ids(
        self, ids: Sequence[str]
    ) -> list[DashboardRecommendation]:
        if not ids:
            return []
        stmt = select(DashboardRecommendation).where(DashboardRecommendation.id.in_(ids))
        return list((await self._session.execute(stmt)).scalars().all())

    async def get_home_snapshot(self) -> DashboardHomeSnapshot | None:
        stmt = select(DashboardHomeSnapshot).where(DashboardHomeSnapshot.id == 1)
        return (await self._session.execute(stmt)).scalar_one_or_none()

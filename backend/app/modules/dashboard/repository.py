from __future__ import annotations

from app.modules.dashboard.models import DashboardHomeSnapshot, DashboardRecommendation
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class DashboardRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_recommendations_ordered(self) -> list[DashboardRecommendation]:
        stmt = select(DashboardRecommendation).order_by(
            DashboardRecommendation.sort_order,
            DashboardRecommendation.id,
        )
        return list((await self._session.execute(stmt)).scalars().all())

    async def get_home_snapshot(self) -> DashboardHomeSnapshot | None:
        stmt = select(DashboardHomeSnapshot).where(DashboardHomeSnapshot.id == 1)
        return (await self._session.execute(stmt)).scalar_one_or_none()

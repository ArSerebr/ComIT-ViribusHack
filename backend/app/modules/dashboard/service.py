from __future__ import annotations

from app.modules.dashboard.models import DashboardRecommendation
from app.modules.dashboard.repository import DashboardRepository
from schemas import DashboardHome, RecommendationCard


def _rec_to_schema(row: DashboardRecommendation) -> RecommendationCard:
    return RecommendationCard(
        id=row.id,
        title=row.title,
        subtitle=row.subtitle,
        image=row.image,
        link=row.link,
    )


class DashboardService:
    def __init__(self, repo: DashboardRepository) -> None:
        self._repo = repo

    async def list_recommendations(self) -> list[RecommendationCard]:
        rows = await self._repo.list_recommendations_ordered()
        return [_rec_to_schema(r) for r in rows]

    async def get_home(self) -> DashboardHome | None:
        snap = await self._repo.get_home_snapshot()
        if snap is None:
            return None
        return DashboardHome.model_validate(snap.home_json)

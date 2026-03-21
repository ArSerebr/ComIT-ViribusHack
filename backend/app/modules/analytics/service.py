from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.repository import AnalyticsRepository


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = AnalyticsRepository(session)

    async def record_like(self, *, entity: str, entity_id: str, ts: int) -> None:
        await self._repo.add_like_event(entity=entity, entity_id=entity_id, ts=ts)
        await self._session.commit()

    async def record_interests(self, *, interests: list[str], ts: int) -> None:
        await self._repo.add_interest_event(interests=interests, ts=ts)
        await self._session.commit()

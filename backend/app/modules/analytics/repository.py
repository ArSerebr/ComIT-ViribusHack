from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.models import AnalyticsInterestEvent, AnalyticsJoinRequest, AnalyticsLikeEvent


class AnalyticsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_like_event(self, *, entity: str, entity_id: str, ts: int) -> None:
        row = AnalyticsLikeEvent(entity=entity, entity_id=entity_id, ts=ts)
        self._session.add(row)
        await self._session.flush()

    async def add_interest_event(self, *, interests: list[str], ts: int) -> None:
        row = AnalyticsInterestEvent(interests=interests, ts=ts)
        self._session.add(row)
        await self._session.flush()

    async def add_join_request(self, *, project_id: str, message: str | None) -> None:
        row = AnalyticsJoinRequest(project_id=project_id, message=message)
        self._session.add(row)
        await self._session.flush()

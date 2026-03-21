from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.analytics import JoinRequestSink
from app.modules.analytics.repository import AnalyticsRepository


class _JoinRequestSink:
    def __init__(self, session: AsyncSession, repo: AnalyticsRepository) -> None:
        self._session = session
        self._repo = repo

    async def record_join_request(self, project_id: str, message: str | None) -> None:
        await self._repo.add_join_request(project_id=project_id, message=message)
        await self._session.commit()


def create_join_request_sink(session: AsyncSession) -> JoinRequestSink:
    return _JoinRequestSink(session, AnalyticsRepository(session))

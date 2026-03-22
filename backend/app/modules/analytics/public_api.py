from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import datetime

from app.contracts.analytics import JoinRequestSink
from app.modules.analytics.repository import AnalyticsRepository
from sqlalchemy.ext.asyncio import AsyncSession


async def get_join_requests_by_applicant_ids(
    session: AsyncSession, applicant_ids: Sequence[uuid.UUID]
) -> list[tuple[int, str, uuid.UUID | None, datetime]]:
    """Return (id, project_id, applicant_user_id, created_at) for given applicants."""
    repo = AnalyticsRepository(session)
    return await repo.get_join_requests_by_applicant_ids(applicant_ids)


class _JoinRequestSink:
    def __init__(self, session: AsyncSession, repo: AnalyticsRepository) -> None:
        self._session = session
        self._repo = repo

    async def record_join_request(
        self,
        project_id: str,
        message: str | None,
        applicant_user_id: uuid.UUID,
    ) -> None:
        await self._repo.add_join_request(
            project_id=project_id,
            message=message,
            applicant_user_id=applicant_user_id,
        )
        await self._session.commit()


def create_join_request_sink(session: AsyncSession) -> JoinRequestSink:
    return _JoinRequestSink(session, AnalyticsRepository(session))


async def record_like_event(
    session: AsyncSession, *, entity: str, entity_id: str, ts: int
) -> None:
    """Record a like event (e.g. recommendation, news). Commits the session."""
    repo = AnalyticsRepository(session)
    await repo.add_like_event(entity=entity, entity_id=entity_id, ts=ts)
    await session.commit()

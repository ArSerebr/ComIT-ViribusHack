from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import datetime

from app.modules.analytics.models import (
    AnalyticsInterestEvent,
    AnalyticsJoinRequest,
    AnalyticsLikeEvent,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


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

    async def add_join_request(
        self,
        *,
        project_id: str,
        message: str | None,
        applicant_user_id: uuid.UUID,
    ) -> None:
        row = AnalyticsJoinRequest(
            project_id=project_id,
            message=message,
            applicant_user_id=applicant_user_id,
        )
        self._session.add(row)
        await self._session.flush()

    async def get_join_requests_by_applicant_ids(
        self, applicant_ids: Sequence[uuid.UUID]
    ) -> list[tuple[int, str, uuid.UUID | None, datetime]]:
        """Return (id, project_id, applicant_user_id, created_at) for given applicants."""
        if not applicant_ids:
            return []
        stmt = (
            select(
                AnalyticsJoinRequest.id,
                AnalyticsJoinRequest.project_id,
                AnalyticsJoinRequest.applicant_user_id,
                AnalyticsJoinRequest.created_at,
            )
            .where(AnalyticsJoinRequest.applicant_user_id.in_(applicant_ids))
            .order_by(AnalyticsJoinRequest.created_at, AnalyticsJoinRequest.id)
        )
        rows = (await self._session.execute(stmt)).all()
        return [(r[0], r[1], r[2], r[3]) for r in rows]

"""Repository: демо-запись на курс."""

from __future__ import annotations

import uuid

from app.modules.agent_demo.models import AgentDemoCourseEnrollment
from sqlalchemy.ext.asyncio import AsyncSession


class AgentDemoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_enrollment(
        self,
        *,
        user_id: uuid.UUID,
        course_slug: str,
        payload: dict | None,
    ) -> AgentDemoCourseEnrollment:
        row = AgentDemoCourseEnrollment(
            user_id=user_id,
            course_slug=course_slug,
            payload=payload,
        )
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return row

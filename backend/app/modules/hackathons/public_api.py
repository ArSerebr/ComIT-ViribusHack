"""Публичный фасад hackathons для других bounded context."""

from __future__ import annotations

from app.modules.hackathons.repository import HackathonRepository
from sqlalchemy.ext.asyncio import AsyncSession


async def count_upcoming_hackathons(session: AsyncSession) -> int:
    """Количество предстоящих мероприятий (хакатонов) в БД."""
    repo = HackathonRepository(session)
    return await repo.count_upcoming()

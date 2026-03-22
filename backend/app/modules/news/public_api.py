"""News public API for cross-module consumption (no ORM leakage)."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from app.modules.news.repository import NewsRepository
from sqlalchemy.ext.asyncio import AsyncSession


async def count_participants_by_user_ids(
    session: AsyncSession, user_ids: Sequence[uuid.UUID]
) -> int:
    """Count participation rows where user_id is in user_ids."""
    repo = NewsRepository(session)
    return await repo.count_participants_by_user_ids(user_ids)


async def list_participations_for_export(
    session: AsyncSession, user_ids: Sequence[uuid.UUID]
) -> list[tuple[uuid.UUID, str, str]]:
    """Return (user_id, featured_id, event_title) for participations of given users."""
    repo = NewsRepository(session)
    return await repo.list_participations_for_export(user_ids)

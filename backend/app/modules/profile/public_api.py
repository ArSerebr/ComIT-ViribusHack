"""Profile public API for cross-module consumption (no ORM leakage)."""

from __future__ import annotations

import uuid
from typing import Sequence

from app.modules.profile.repository import ProfileRepository
from sqlalchemy.ext.asyncio import AsyncSession


async def get_display_names_by_user_ids(
    session: AsyncSession, user_ids: Sequence[uuid.UUID]
) -> dict[uuid.UUID, str | None]:
    """Return user_id -> display_name for given user IDs."""
    repo = ProfileRepository(session)
    return await repo.get_display_names_by_user_ids(user_ids)


async def get_profiles_by_university(
    session: AsyncSession, university_id: str
) -> list[tuple[uuid.UUID, str | None]]:
    """Return (user_id, display_name) for profiles with this university."""
    repo = ProfileRepository(session)
    return await repo.get_profiles_by_university(university_id)


async def count_interests_by_university(
    session: AsyncSession, university_id: str
) -> int:
    """Count total interest links for users in this university."""
    repo = ProfileRepository(session)
    return await repo.count_interests_by_university(university_id)


async def list_universities(
    session: AsyncSession,
) -> list[tuple[str, str]]:
    """Return (id, name) for all universities, ordered."""
    repo = ProfileRepository(session)
    rows = await repo.list_universities_ordered()
    return [(r.id, r.name) for r in rows]

from __future__ import annotations

import uuid

from app.modules.profile.models import UserProfile, UserProfileInterest
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession


class ProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_profile(self, user_id: uuid.UUID) -> UserProfile | None:
        stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def get_or_create_profile(self, user_id: uuid.UUID) -> tuple[UserProfile, bool]:
        row = await self.get_profile(user_id)
        if row is not None:
            return row, False
        created = UserProfile(user_id=user_id)
        self._session.add(created)
        await self._session.flush()
        return created, True

    async def list_interest_ids(self, user_id: uuid.UUID) -> list[str]:
        stmt = select(UserProfileInterest.interest_id).where(UserProfileInterest.user_id == user_id)
        rows = (await self._session.execute(stmt)).scalars().all()
        return sorted(str(x) for x in rows)

    async def replace_interests(self, user_id: uuid.UUID, interest_ids: list[str]) -> None:
        await self._session.execute(
            delete(UserProfileInterest).where(UserProfileInterest.user_id == user_id)
        )
        for iid in interest_ids:
            self._session.add(UserProfileInterest(user_id=user_id, interest_id=iid))
        await self._session.flush()

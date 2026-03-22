from __future__ import annotations

import uuid

from app.modules.profile.models import ProfileUniversity, UserProfile, UserProfileInterest
from sqlalchemy import delete, func, select
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

    async def add_interests(self, user_id: uuid.UUID, interest_ids: list[str]) -> None:
        """Добавить интересы; дубликаты во входе и уже существующие связи пропускаются."""
        if not interest_ids:
            return
        seen: set[str] = set()
        ordered_unique: list[str] = []
        for iid in interest_ids:
            if iid not in seen:
                seen.add(iid)
                ordered_unique.append(iid)
        existing = frozenset(await self.list_interest_ids(user_id))
        for iid in ordered_unique:
            if iid not in existing:
                self._session.add(UserProfileInterest(user_id=user_id, interest_id=iid))
        await self._session.flush()

    # --- University ---

    async def get_university(self, university_id: str) -> ProfileUniversity | None:
        stmt = select(ProfileUniversity).where(ProfileUniversity.id == university_id)
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def list_universities_ordered(self) -> list[ProfileUniversity]:
        stmt = select(ProfileUniversity).order_by(
            ProfileUniversity.sort_order,
            ProfileUniversity.id,
        )
        return list((await self._session.execute(stmt)).scalars().all())

    async def university_ids_exist(self, ids: list[str]) -> bool:
        unique = frozenset(ids)
        if not unique:
            return True
        stmt = (
            select(func.count())
            .select_from(ProfileUniversity)
            .where(ProfileUniversity.id.in_(unique))
        )
        n = (await self._session.execute(stmt)).scalar_one()
        return int(n) == len(unique)

    async def create_university(self, row: ProfileUniversity) -> ProfileUniversity:
        self._session.add(row)
        await self._session.flush()
        return row

    async def update_university(
        self, university_id: str, name: str | None = None, sort_order: int | None = None
    ) -> ProfileUniversity | None:
        row = await self.get_university(university_id)
        if row is None:
            return None
        if name is not None:
            row.name = name
        if sort_order is not None:
            row.sort_order = sort_order
        await self._session.flush()
        return row

    async def delete_university(self, university_id: str) -> bool:
        row = await self.get_university(university_id)
        if row is None:
            return False
        await self._session.delete(row)
        await self._session.flush()
        return True

    async def count_profiles_with_university(self, university_id: str) -> int:
        stmt = (
            select(func.count())
            .select_from(UserProfile)
            .where(UserProfile.university_id == university_id)
        )
        return int((await self._session.execute(stmt)).scalar_one())

    async def get_profiles_by_university(
        self, university_id: str
    ) -> list[tuple[uuid.UUID, str | None]]:
        """Return (user_id, display_name) for profiles with this university."""
        stmt = (
            select(UserProfile.user_id, UserProfile.display_name)
            .where(UserProfile.university_id == university_id)
            .order_by(UserProfile.user_id)
        )
        rows = (await self._session.execute(stmt)).all()
        return [(r[0], r[1]) for r in rows]

    async def count_interests_by_university(self, university_id: str) -> int:
        """Count total interest links for users in this university."""
        stmt = (
            select(func.count())
            .select_from(UserProfileInterest)
            .join(UserProfile, UserProfile.user_id == UserProfileInterest.user_id)
            .where(UserProfile.university_id == university_id)
        )
        return int((await self._session.execute(stmt)).scalar_one() or 0)

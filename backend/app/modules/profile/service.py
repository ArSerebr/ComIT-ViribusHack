from __future__ import annotations

import uuid
from typing import Literal

from app.contracts.library import InterestCatalogPort
from app.modules.profile.models import ProfileUniversity
from app.modules.profile.repository import ProfileRepository
from app.modules.profile.schemas import UniversityCreateBody, UniversityUpdateBody
from fastapi import HTTPException
from schemas import (
    ProfileInterest,
    ProfileInterestsAdd,
    ProfileMe,
    ProfileMePatch,
    ProfileUniversityOut,
)
from sqlalchemy.ext.asyncio import AsyncSession


class ProfileService:
    def __init__(
        self,
        session: AsyncSession,
        repo: ProfileRepository,
        interest_catalog: InterestCatalogPort,
    ) -> None:
        self._session = session
        self._repo = repo
        self._interest_catalog = interest_catalog

    async def get_me(self, user_id: uuid.UUID) -> ProfileMe:
        profile, created = await self._repo.get_or_create_profile(user_id)
        if created:
            await self._session.commit()
        university: ProfileUniversityOut | None = None
        if profile.university_id:
            uni = await self._repo.get_university(profile.university_id)
            if uni is not None:
                university = ProfileUniversityOut(id=uni.id, name=uni.name)
        interest_ids = await self._repo.list_interest_ids(user_id)
        labels = await self._interest_catalog.labels_for_interest_ids(interest_ids)
        interests = [
            ProfileInterest(id=iid, label=labels[iid]) for iid in interest_ids if iid in labels
        ]
        return ProfileMe(
            displayName=profile.display_name,
            bio=profile.bio,
            university=university,
            interests=interests,
        )

    async def patch_me(self, user_id: uuid.UUID, body: ProfileMePatch) -> ProfileMe:
        data = body.model_dump(exclude_unset=True)
        if "interestIds" in data:
            ok = await self._interest_catalog.all_interest_option_ids_exist(data["interestIds"])
            if not ok:
                raise HTTPException(status_code=400, detail="Unknown interest id")
        if "universityId" in data:
            uid_val = data["universityId"]
            if uid_val is not None and uid_val != "":
                ok = await self._repo.university_ids_exist([uid_val])
                if not ok:
                    raise HTTPException(status_code=400, detail="Unknown university id")

        profile, _ = await self._repo.get_or_create_profile(user_id)
        if "displayName" in data:
            profile.display_name = data["displayName"]
        if "bio" in data:
            profile.bio = data["bio"]
        if "universityId" in data:
            profile.university_id = data["universityId"] if data["universityId"] else None
        if "interestIds" in data:
            await self._repo.replace_interests(user_id, list(data["interestIds"]))

        await self._session.commit()
        return await self.get_me(user_id)

    async def list_universities(self) -> list[ProfileUniversityOut]:
        rows = await self._repo.list_universities_ordered()
        return [ProfileUniversityOut(id=r.id, name=r.name) for r in rows]

    async def add_interests(self, user_id: uuid.UUID, body: ProfileInterestsAdd) -> ProfileMe:
        ok = await self._interest_catalog.all_interest_option_ids_exist(body.interestIds)
        if not ok:
            raise HTTPException(status_code=400, detail="Unknown interest id")
        _, _ = await self._repo.get_or_create_profile(user_id)
        await self._repo.add_interests(user_id, list(body.interestIds))
        await self._session.commit()
        return await self.get_me(user_id)

    # --- Admin: Universities ---

    async def admin_list_universities(self) -> list[ProfileUniversityOut]:
        rows = await self._repo.list_universities_ordered()
        return [ProfileUniversityOut(id=r.id, name=r.name) for r in rows]

    async def admin_create_university(
        self, body: UniversityCreateBody
    ) -> tuple[Literal["ok", "exists"], ProfileUniversityOut | None]:
        if await self._repo.get_university(body.id) is not None:
            return ("exists", None)
        sort_order = body.sort_order if body.sort_order is not None else 0
        row = ProfileUniversity(id=body.id, name=body.name, sort_order=sort_order)
        await self._repo.create_university(row)
        await self._session.commit()
        return ("ok", ProfileUniversityOut(id=row.id, name=row.name))

    async def admin_update_university(
        self, university_id: str, body: UniversityUpdateBody
    ) -> tuple[Literal["ok", "not_found"], ProfileUniversityOut | None]:
        row = await self._repo.update_university(
            university_id,
            name=body.name,
            sort_order=body.sort_order,
        )
        if row is None:
            return ("not_found", None)
        await self._session.commit()
        return ("ok", ProfileUniversityOut(id=row.id, name=row.name))

    async def admin_delete_university(
        self, university_id: str
    ) -> Literal["ok", "not_found", "in_use"]:
        if await self._repo.get_university(university_id) is None:
            return "not_found"
        n = await self._repo.count_profiles_with_university(university_id)
        if n > 0:
            return "in_use"
        await self._repo.delete_university(university_id)
        await self._session.commit()
        return "ok"

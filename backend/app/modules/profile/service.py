from __future__ import annotations

import uuid

from app.contracts.library import InterestCatalogPort
from app.modules.profile.repository import ProfileRepository
from fastapi import HTTPException
from schemas import ProfileInterest, ProfileMe, ProfileMePatch
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
        interest_ids = await self._repo.list_interest_ids(user_id)
        labels = await self._interest_catalog.labels_for_interest_ids(interest_ids)
        interests = [
            ProfileInterest(id=iid, label=labels[iid]) for iid in interest_ids if iid in labels
        ]
        return ProfileMe(
            displayName=profile.display_name,
            bio=profile.bio,
            interests=interests,
        )

    async def patch_me(self, user_id: uuid.UUID, body: ProfileMePatch) -> ProfileMe:
        data = body.model_dump(exclude_unset=True)
        if "interestIds" in data:
            ok = await self._interest_catalog.all_interest_option_ids_exist(data["interestIds"])
            if not ok:
                raise HTTPException(status_code=400, detail="Unknown interest id")

        profile, _ = await self._repo.get_or_create_profile(user_id)
        if "displayName" in data:
            profile.display_name = data["displayName"]
        if "bio" in data:
            profile.bio = data["bio"]
        if "interestIds" in data:
            await self._repo.replace_interests(user_id, list(data["interestIds"]))

        await self._session.commit()
        return await self.get_me(user_id)

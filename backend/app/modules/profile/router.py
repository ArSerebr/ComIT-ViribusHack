"""Profile HTTP: текущий пользователь."""

from __future__ import annotations

import uuid

from app.modules.auth.deps import current_active_user
from app.modules.auth.models import User
from app.modules.profile.deps import get_profile_service
from app.modules.profile.service import ProfileService
from fastapi import APIRouter, Depends
from schemas import ProfileInterestsAdd, ProfileMe, ProfileMePatch

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("/me", response_model=ProfileMe)
async def get_my_profile(
    user: User = Depends(current_active_user),
    service: ProfileService = Depends(get_profile_service),
):
    uid = user.id
    if not isinstance(uid, uuid.UUID):
        uid = uuid.UUID(str(uid))
    return await service.get_me(uid)


@router.patch("/me", response_model=ProfileMe)
async def patch_my_profile(
    body: ProfileMePatch,
    user: User = Depends(current_active_user),
    service: ProfileService = Depends(get_profile_service),
):
    uid = user.id
    if not isinstance(uid, uuid.UUID):
        uid = uuid.UUID(str(uid))
    return await service.patch_me(uid, body)


@router.post("/me/interests", response_model=ProfileMe)
async def post_my_profile_interests(
    body: ProfileInterestsAdd,
    user: User = Depends(current_active_user),
    service: ProfileService = Depends(get_profile_service),
):
    """Добавить интересы к профилю (уже выбранные и дубликаты в теле запроса игнорируются)."""
    uid = user.id
    if not isinstance(uid, uuid.UUID):
        uid = uuid.UUID(str(uid))
    return await service.add_interests(uid, body)

"""Moderator/admin: profile universities CRUD."""

from __future__ import annotations

from app.modules.auth.deps import require_roles
from app.modules.auth.models import User
from app.modules.profile.deps import get_profile_service
from app.modules.profile.schemas import UniversityCreateBody, UniversityUpdateBody
from app.modules.profile.service import ProfileService
from fastapi import APIRouter, Depends, HTTPException, Response
from schemas import ErrorDetail, ProfileUniversityOut

router = APIRouter(prefix="/api/admin/profile", tags=["profile-admin"])


@router.get("/universities", response_model=list[ProfileUniversityOut])
async def admin_list_universities(
    _: User = Depends(require_roles("moderator", "admin")),
    service: ProfileService = Depends(get_profile_service),
) -> list[ProfileUniversityOut]:
    """Список университетов для админки."""
    return await service.admin_list_universities()


@router.post(
    "/universities",
    response_model=ProfileUniversityOut,
    responses={409: {"description": "Уже существует", "model": ErrorDetail}},
)
async def admin_create_university(
    body: UniversityCreateBody,
    _: User = Depends(require_roles("moderator", "admin")),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileUniversityOut:
    status, item = await service.admin_create_university(body)
    if status == "exists":
        raise HTTPException(status_code=409, detail="University already exists")
    assert item is not None
    return item


@router.patch("/universities/{university_id}", response_model=ProfileUniversityOut)
async def admin_update_university(
    university_id: str,
    body: UniversityUpdateBody,
    _: User = Depends(require_roles("moderator", "admin")),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileUniversityOut:
    status, item = await service.admin_update_university(university_id, body)
    if status == "not_found":
        raise HTTPException(status_code=404, detail="University not found")
    assert item is not None
    return item


@router.delete("/universities/{university_id}", status_code=204, response_class=Response)
async def admin_delete_university(
    university_id: str,
    _: User = Depends(require_roles("moderator", "admin")),
    service: ProfileService = Depends(get_profile_service),
) -> Response:
    st = await service.admin_delete_university(university_id)
    if st == "not_found":
        raise HTTPException(status_code=404, detail="University not found")
    if st == "in_use":
        raise HTTPException(status_code=409, detail="University is in use")
    return Response(status_code=204)

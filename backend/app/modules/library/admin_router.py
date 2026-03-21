"""Moderator/admin: showcase, interest catalog, tags."""

from __future__ import annotations

from app.modules.auth.deps import require_roles
from app.modules.auth.models import User
from app.modules.library.deps import get_library_service
from app.modules.library.schemas import (
    InterestOptionCreateBody,
    InterestOptionUpdateBody,
    LibraryTagCreateBody,
    LibraryTagUpdateBody,
    ShowcaseCreateBody,
    ShowcaseUpdateBody,
)
from app.modules.library.service import LibraryService
from fastapi import APIRouter, Depends, HTTPException, Response
from schemas import ArticleTag, ErrorDetail, InterestOption, LibraryShowcaseItem

router = APIRouter(prefix="/api/admin/library", tags=["library-admin"])


# --- Showcase ---


@router.post(
    "/showcase",
    response_model=LibraryShowcaseItem,
    responses={409: {"description": "Уже существует", "model": ErrorDetail}},
)
async def admin_create_showcase(
    body: ShowcaseCreateBody,
    _: User = Depends(require_roles("moderator", "admin")),
    service: LibraryService = Depends(get_library_service),
) -> LibraryShowcaseItem:
    status, item = await service.admin_create_showcase(body)
    if status == "exists":
        raise HTTPException(status_code=409, detail="Showcase item already exists")
    assert item is not None
    return item


@router.patch("/showcase/{item_id}", response_model=LibraryShowcaseItem)
async def admin_update_showcase(
    item_id: str,
    body: ShowcaseUpdateBody,
    _: User = Depends(require_roles("moderator", "admin")),
    service: LibraryService = Depends(get_library_service),
) -> LibraryShowcaseItem:
    status, item = await service.admin_update_showcase(item_id, body)
    if status == "not_found":
        raise HTTPException(status_code=404, detail="Showcase item not found")
    assert item is not None
    return item


@router.delete("/showcase/{item_id}", status_code=204, response_class=Response)
async def admin_delete_showcase(
    item_id: str,
    _: User = Depends(require_roles("moderator", "admin")),
    service: LibraryService = Depends(get_library_service),
) -> Response:
    st = await service.admin_delete_showcase(item_id)
    if st == "not_found":
        raise HTTPException(status_code=404, detail="Showcase item not found")
    return Response(status_code=204)


# --- Interests ---


@router.post(
    "/interests",
    response_model=InterestOption,
    responses={409: {"description": "Уже существует", "model": ErrorDetail}},
)
async def admin_create_interest(
    body: InterestOptionCreateBody,
    _: User = Depends(require_roles("moderator", "admin")),
    service: LibraryService = Depends(get_library_service),
) -> InterestOption:
    status, opt = await service.admin_create_interest(body)
    if status == "exists":
        raise HTTPException(status_code=409, detail="Interest option already exists")
    assert opt is not None
    return opt


@router.patch("/interests/{interest_id}", response_model=InterestOption)
async def admin_update_interest(
    interest_id: str,
    body: InterestOptionUpdateBody,
    _: User = Depends(require_roles("moderator", "admin")),
    service: LibraryService = Depends(get_library_service),
) -> InterestOption:
    status, opt = await service.admin_update_interest(interest_id, body)
    if status == "not_found":
        raise HTTPException(status_code=404, detail="Interest option not found")
    assert opt is not None
    return opt


@router.delete("/interests/{interest_id}", status_code=204, response_class=Response)
async def admin_delete_interest(
    interest_id: str,
    _: User = Depends(require_roles("moderator", "admin")),
    service: LibraryService = Depends(get_library_service),
) -> Response:
    st = await service.admin_delete_interest(interest_id)
    if st == "not_found":
        raise HTTPException(status_code=404, detail="Interest option not found")
    return Response(status_code=204)


# --- Tags ---


@router.post(
    "/tags",
    response_model=ArticleTag,
    responses={409: {"description": "Уже существует", "model": ErrorDetail}},
)
async def admin_create_tag(
    body: LibraryTagCreateBody,
    _: User = Depends(require_roles("moderator", "admin")),
    service: LibraryService = Depends(get_library_service),
) -> ArticleTag:
    status, tag = await service.admin_create_tag(body)
    if status == "exists":
        raise HTTPException(status_code=409, detail="Tag already exists")
    assert tag is not None
    return tag


@router.patch("/tags/{tag_id}", response_model=ArticleTag)
async def admin_update_tag(
    tag_id: str,
    body: LibraryTagUpdateBody,
    _: User = Depends(require_roles("moderator", "admin")),
    service: LibraryService = Depends(get_library_service),
) -> ArticleTag:
    status, tag = await service.admin_update_tag(tag_id, body)
    if status == "not_found":
        raise HTTPException(status_code=404, detail="Tag not found")
    assert tag is not None
    return tag


@router.delete("/tags/{tag_id}", status_code=204, response_class=Response)
async def admin_delete_tag(
    tag_id: str,
    _: User = Depends(require_roles("moderator", "admin")),
    service: LibraryService = Depends(get_library_service),
) -> Response:
    st = await service.admin_delete_tag(tag_id)
    if st == "not_found":
        raise HTTPException(status_code=404, detail="Tag not found")
    if st == "in_use":
        raise HTTPException(status_code=409, detail="Tag is in use")
    return Response(status_code=204)

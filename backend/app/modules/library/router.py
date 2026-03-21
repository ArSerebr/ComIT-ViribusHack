"""Library HTTP adapter: thin router → service only. No DB/repo access."""

from __future__ import annotations

from app.modules.auth.deps import current_active_user
from app.modules.auth.models import User
from app.modules.library.deps import get_library_service
from app.modules.library.schemas import LibraryArticleCreateBody, LibraryArticleUpdateBody
from app.modules.library.service import LibraryService
from fastapi import APIRouter, Depends, HTTPException, Response
from schemas import ErrorDetail, LibraryArticle, LibraryBundle

router = APIRouter(prefix="/api", tags=["library"])


@router.get("/library", response_model=LibraryBundle)
async def get_library(service: LibraryService = Depends(get_library_service)):
    return await service.get_bundle()


@router.post(
    "/library/articles",
    response_model=LibraryArticle,
    responses={
        409: {"description": "Статья уже существует", "model": ErrorDetail},
        400: {"description": "Неизвестные теги", "model": ErrorDetail},
    },
)
async def create_library_article(
    body: LibraryArticleCreateBody,
    user: User = Depends(current_active_user),
    service: LibraryService = Depends(get_library_service),
) -> LibraryArticle:
    status, art = await service.create_article(user, body)
    if status == "exists":
        raise HTTPException(status_code=409, detail="Article already exists")
    if status == "bad_tags":
        raise HTTPException(status_code=400, detail="Unknown tag ids")
    assert art is not None
    return art


@router.patch(
    "/library/articles/{article_id}",
    response_model=LibraryArticle,
    responses={
        404: {"description": "Не найдено", "model": ErrorDetail},
        403: {"description": "Нет прав", "model": ErrorDetail},
        400: {"description": "Неизвестные теги", "model": ErrorDetail},
    },
)
async def patch_library_article(
    article_id: str,
    body: LibraryArticleUpdateBody,
    user: User = Depends(current_active_user),
    service: LibraryService = Depends(get_library_service),
) -> LibraryArticle:
    status, art = await service.update_article(user, article_id, body)
    if status == "not_found":
        raise HTTPException(status_code=404, detail="Article not found")
    if status == "forbidden":
        raise HTTPException(status_code=403, detail="Forbidden")
    if status == "bad_tags":
        raise HTTPException(status_code=400, detail="Unknown tag ids")
    assert art is not None
    return art


@router.delete(
    "/library/articles/{article_id}",
    status_code=204,
    response_class=Response,
    responses={
        404: {"description": "Не найдено", "model": ErrorDetail},
        403: {"description": "Нет прав", "model": ErrorDetail},
    },
)
async def delete_library_article(
    article_id: str,
    user: User = Depends(current_active_user),
    service: LibraryService = Depends(get_library_service),
) -> Response:
    st = await service.delete_article(user, article_id)
    if st == "not_found":
        raise HTTPException(status_code=404, detail="Article not found")
    if st == "forbidden":
        raise HTTPException(status_code=403, detail="Forbidden")
    return Response(status_code=204)

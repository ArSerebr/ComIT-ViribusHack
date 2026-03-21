"""News HTTP adapter: thin router → service only. No DB/repo access."""

from __future__ import annotations

from app.modules.auth.deps import current_active_user
from app.modules.auth.models import User
from app.modules.news.deps import get_news_service
from app.modules.news.schemas import (
    NewsFeaturedCreateBody,
    NewsFeaturedUpdateBody,
    NewsMiniCreateBody,
    NewsMiniUpdateBody,
)
from app.modules.news.service import NewsService
from fastapi import APIRouter, Depends, HTTPException, Response
from schemas import ErrorDetail, FeaturedNewsItem, NewsMiniItem

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/mini", response_model=list[NewsMiniItem])
async def get_news_mini(service: NewsService = Depends(get_news_service)):
    return await service.list_mini()


@router.post(
    "/mini",
    response_model=NewsMiniItem,
    responses={409: {"description": "Уже существует", "model": ErrorDetail}},
)
async def create_news_mini(
    body: NewsMiniCreateBody,
    user: User = Depends(current_active_user),
    service: NewsService = Depends(get_news_service),
) -> NewsMiniItem:
    status, item = await service.create_news_mini(user, body)
    if status == "exists":
        raise HTTPException(status_code=409, detail="News item already exists")
    assert item is not None
    return item


@router.patch(
    "/mini/{news_id}",
    response_model=NewsMiniItem,
    responses={
        404: {"description": "Не найдено", "model": ErrorDetail},
        403: {"description": "Нет прав", "model": ErrorDetail},
    },
)
async def patch_news_mini(
    news_id: str,
    body: NewsMiniUpdateBody,
    user: User = Depends(current_active_user),
    service: NewsService = Depends(get_news_service),
) -> NewsMiniItem:
    status, item = await service.update_news_mini(user, news_id, body)
    if status == "not_found":
        raise HTTPException(status_code=404, detail="News not found")
    if status == "forbidden":
        raise HTTPException(status_code=403, detail="Forbidden")
    assert item is not None
    return item


@router.delete(
    "/mini/{news_id}",
    status_code=204,
    response_class=Response,
    responses={
        404: {"description": "Не найдено", "model": ErrorDetail},
        403: {"description": "Нет прав", "model": ErrorDetail},
    },
)
async def delete_news_mini(
    news_id: str,
    user: User = Depends(current_active_user),
    service: NewsService = Depends(get_news_service),
) -> Response:
    st = await service.delete_news_mini(user, news_id)
    if st == "not_found":
        raise HTTPException(status_code=404, detail="News not found")
    if st == "forbidden":
        raise HTTPException(status_code=403, detail="Forbidden")
    return Response(status_code=204)


@router.get("/featured", response_model=list[FeaturedNewsItem])
async def get_news_featured(service: NewsService = Depends(get_news_service)):
    return await service.list_featured()


@router.post(
    "/featured",
    response_model=FeaturedNewsItem,
    responses={
        409: {"description": "Уже существует", "model": ErrorDetail},
        403: {"description": "Только модератор", "model": ErrorDetail},
    },
)
async def create_news_featured(
    body: NewsFeaturedCreateBody,
    user: User = Depends(current_active_user),
    service: NewsService = Depends(get_news_service),
) -> FeaturedNewsItem:
    status, item = await service.create_news_featured(user, body)
    if status == "forbidden":
        raise HTTPException(status_code=403, detail="Forbidden")
    if status == "exists":
        raise HTTPException(status_code=409, detail="Featured news already exists")
    assert item is not None
    return item


@router.patch(
    "/featured/{news_id}",
    response_model=FeaturedNewsItem,
    responses={
        404: {"description": "Не найдено", "model": ErrorDetail},
        403: {"description": "Только модератор", "model": ErrorDetail},
    },
)
async def patch_news_featured(
    news_id: str,
    body: NewsFeaturedUpdateBody,
    user: User = Depends(current_active_user),
    service: NewsService = Depends(get_news_service),
) -> FeaturedNewsItem:
    status, item = await service.update_news_featured(user, news_id, body)
    if status == "forbidden":
        raise HTTPException(status_code=403, detail="Forbidden")
    if status == "not_found":
        raise HTTPException(status_code=404, detail="News not found")
    assert item is not None
    return item


@router.delete(
    "/featured/{news_id}",
    status_code=204,
    response_class=Response,
    responses={
        404: {"description": "Не найдено", "model": ErrorDetail},
        403: {"description": "Только модератор", "model": ErrorDetail},
    },
)
async def delete_news_featured(
    news_id: str,
    user: User = Depends(current_active_user),
    service: NewsService = Depends(get_news_service),
) -> Response:
    st = await service.delete_news_featured(user, news_id)
    if st == "forbidden":
        raise HTTPException(status_code=403, detail="Forbidden")
    if st == "not_found":
        raise HTTPException(status_code=404, detail="News not found")
    return Response(status_code=204)

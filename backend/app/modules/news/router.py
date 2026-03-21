"""News HTTP adapter: thin router → service only. No DB/repo access."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.modules.news.deps import get_news_service
from app.modules.news.service import NewsService
from schemas import FeaturedNewsItem, NewsMiniItem

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/mini", response_model=list[NewsMiniItem])
async def get_news_mini(service: NewsService = Depends(get_news_service)):
    return await service.list_mini()


@router.get("/featured", response_model=list[FeaturedNewsItem])
async def get_news_featured(service: NewsService = Depends(get_news_service)):
    return await service.list_featured()

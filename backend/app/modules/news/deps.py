from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.modules.news.repository import NewsRepository
from app.modules.news.service import NewsService


async def get_news_service(session: AsyncSession = Depends(get_db)) -> NewsService:
    return NewsService(NewsRepository(session))

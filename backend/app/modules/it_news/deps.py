from __future__ import annotations

from app.core.db.session import get_db
from app.modules.it_news.repository import ItNewsRepository
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


def get_it_news_repository(session: AsyncSession = Depends(get_db)) -> ItNewsRepository:
    return ItNewsRepository(session)

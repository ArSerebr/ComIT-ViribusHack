"""University analytics dependencies."""

from __future__ import annotations

from app.core.db.session import get_db
from app.modules.university_analytics.service import UniversityAnalyticsService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_university_analytics_service(
    session: AsyncSession = Depends(get_db),
) -> UniversityAnalyticsService:
    return UniversityAnalyticsService(session)

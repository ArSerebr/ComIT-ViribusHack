"""Recommendations module dependencies."""

from __future__ import annotations

from app.core.db.session import get_db
from app.modules.recommendations.ml_client import MLRecommendationClient
from app.modules.recommendations.service import RecommendationsService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_recommendations_service(
    session: AsyncSession = Depends(get_db),
) -> RecommendationsService:
    return RecommendationsService(session, ml_client=MLRecommendationClient())

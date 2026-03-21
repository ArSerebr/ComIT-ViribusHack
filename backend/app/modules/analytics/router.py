"""Analytics HTTP adapter: thin router → service only. No DB/repo access."""

from __future__ import annotations

from app.modules.analytics.deps import get_analytics_service
from app.modules.analytics.schemas import InterestsPayload, LikePayload, OkResponse
from app.modules.analytics.service import AnalyticsService
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api", tags=["analytics"])


@router.post("/recommendations/like", response_model=OkResponse)
async def post_recommendation_like(
    body: LikePayload,
    service: AnalyticsService = Depends(get_analytics_service),
) -> OkResponse:
    await service.record_like(entity=body.entity, entity_id=body.id, ts=body.ts)
    return OkResponse(ok=True)


@router.post("/library/interests", response_model=OkResponse)
async def post_library_interests(
    body: InterestsPayload,
    service: AnalyticsService = Depends(get_analytics_service),
) -> OkResponse:
    await service.record_interests(interests=body.interests, ts=body.ts)
    return OkResponse(ok=True)

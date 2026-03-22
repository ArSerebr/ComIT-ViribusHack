"""Recommendations HTTP adapter: thin router → service only."""

from __future__ import annotations

from app.modules.auth.deps import current_active_user
from app.modules.recommendations.deps import get_recommendations_service
from app.modules.recommendations.schemas import FeedbackPayload
from app.modules.recommendations.service import RecommendationsService
from fastapi import APIRouter, Depends
from schemas import OkResponse

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.post("/feedback", response_model=OkResponse)
async def post_recommendations_feedback(
    body: FeedbackPayload,
    service: RecommendationsService = Depends(get_recommendations_service),
    user=Depends(current_active_user),
) -> OkResponse:
    """
    Record user reaction (open, like, share, etc.) for ML adaptation
    and analytics. Requires authentication.
    """
    await service.record_feedback(
        user_id=user.id,
        entity_id=body.entity_id,
        reaction=body.reaction,
        ts=body.ts,
    )
    return OkResponse(ok=True)

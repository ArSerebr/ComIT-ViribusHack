"""Dashboard HTTP adapter: thin router → service only. No DB/repo access."""

from __future__ import annotations

from app.modules.auth.deps import current_user_optional
from app.modules.dashboard.deps import get_dashboard_service
from app.modules.dashboard.service import DashboardService
from app.modules.recommendations.deps import get_recommendations_service
from app.modules.recommendations.service import RecommendationsService
from fastapi import APIRouter, Depends, HTTPException
from schemas import DashboardHome, ErrorDetail, RecommendationCard

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/recommendations", response_model=list[RecommendationCard])
async def get_dashboard_recommendations(
    rec_service: RecommendationsService = Depends(get_recommendations_service),
    user=Depends(current_user_optional),
):
    """Personalized recommendations via ML for auth users, static fallback otherwise."""
    return await rec_service.list_recommendations(
        user_id=user.id if user else None,
        limit=10,
    )


@router.get(
    "/home",
    response_model=DashboardHome,
    responses={404: {"description": "Конфиг главной не задан", "model": ErrorDetail}},
)
async def get_dashboard_home(service: DashboardService = Depends(get_dashboard_service)):
    home = await service.get_home()
    if home is None:
        raise HTTPException(status_code=404, detail="Dashboard home not configured")
    return home

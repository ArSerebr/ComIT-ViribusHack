"""Dashboard HTTP adapter: thin router → service only. No DB/repo access."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.modules.dashboard.deps import get_dashboard_service
from app.modules.dashboard.service import DashboardService
from schemas import DashboardHome, ErrorDetail, RecommendationCard

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/recommendations", response_model=list[RecommendationCard])
async def get_dashboard_recommendations(
    service: DashboardService = Depends(get_dashboard_service),
):
    return await service.list_recommendations()


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

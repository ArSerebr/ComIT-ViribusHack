"""University analytics HTTP: public endpoints, no auth."""

from __future__ import annotations

from app.modules.university_analytics.deps import get_university_analytics_service
from app.modules.university_analytics.schemas import (
    UniversityDashboard,
    UniversityListItem,
)
from app.modules.university_analytics.service import UniversityAnalyticsService
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

router = APIRouter(prefix="/api/analytics", tags=["university_analytics"])


@router.get(
    "/universities",
    response_model=list[UniversityListItem],
)
async def list_universities_with_metrics(
    service: UniversityAnalyticsService = Depends(get_university_analytics_service),
):
    """List universities with aggregated metrics (public, no auth)."""
    return await service.list_universities_with_metrics()


@router.get(
    "/universities/{university_id}/dashboard",
    response_model=UniversityDashboard,
)
async def get_university_dashboard(
    university_id: str,
    service: UniversityAnalyticsService = Depends(get_university_analytics_service),
):
    """Dashboard for a single university (public, no auth)."""
    dash = await service.get_dashboard(university_id)
    if dash is None:
        raise HTTPException(status_code=404, detail="University not found")
    return dash


@router.get(
    "/universities/{university_id}/export/students",
    response_class=Response,
)
async def export_students_csv(
    university_id: str,
    service: UniversityAnalyticsService = Depends(get_university_analytics_service),
):
    """Export students CSV for university (public, no auth)."""
    content = await service.export_students_csv(university_id)
    if content is None:
        raise HTTPException(status_code=404, detail="University not found")
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="students_{university_id}.csv"'
        },
    )


@router.get(
    "/universities/{university_id}/export/participation",
    response_class=Response,
)
async def export_participation_csv(
    university_id: str,
    service: UniversityAnalyticsService = Depends(get_university_analytics_service),
):
    """Export event participation CSV (public, no auth)."""
    content = await service.export_participation_csv(university_id)
    if content is None:
        raise HTTPException(status_code=404, detail="University not found")
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="participation_{university_id}.csv"'
        },
    )


@router.get(
    "/universities/{university_id}/export/projects",
    response_class=Response,
)
async def export_projects_csv(
    university_id: str,
    service: UniversityAnalyticsService = Depends(get_university_analytics_service),
):
    """Export projects CSV (public, no auth)."""
    content = await service.export_projects_csv(university_id)
    if content is None:
        raise HTTPException(status_code=404, detail="University not found")
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="projects_{university_id}.csv"'
        },
    )


@router.get(
    "/universities/{university_id}/export/articles",
    response_class=Response,
)
async def export_articles_csv(
    university_id: str,
    service: UniversityAnalyticsService = Depends(get_university_analytics_service),
):
    """Export articles CSV (public, no auth)."""
    content = await service.export_articles_csv(university_id)
    if content is None:
        raise HTTPException(status_code=404, detail="University not found")
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="articles_{university_id}.csv"'
        },
    )


@router.get(
    "/universities/{university_id}/export/join-requests",
    response_class=Response,
)
async def export_join_requests_csv(
    university_id: str,
    service: UniversityAnalyticsService = Depends(get_university_analytics_service),
):
    """Export join requests CSV (public, no auth)."""
    content = await service.export_join_requests_csv(university_id)
    if content is None:
        raise HTTPException(status_code=404, detail="University not found")
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="join_requests_{university_id}.csv"'
        },
    )

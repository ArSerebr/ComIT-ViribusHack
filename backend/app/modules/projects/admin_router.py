"""Moderator/admin: kanban columns."""

from __future__ import annotations

from app.modules.auth.deps import require_roles
from app.modules.auth.models import User
from app.modules.projects.deps import get_projects_service
from app.modules.projects.schemas import ProjectsColumnCreate, ProjectsColumnUpdate
from app.modules.projects.service import ProjectsService
from fastapi import APIRouter, Depends, HTTPException, Response
from schemas import ErrorDetail, ProjectColumn

router = APIRouter(prefix="/api/admin/projects/columns", tags=["projects-admin"])


@router.post(
    "",
    response_model=ProjectColumn,
    responses={409: {"description": "Колонка уже существует", "model": ErrorDetail}},
)
async def admin_create_column(
    body: ProjectsColumnCreate,
    _: User = Depends(require_roles("moderator", "admin")),
    service: ProjectsService = Depends(get_projects_service),
) -> ProjectColumn:
    status, col = await service.admin_create_column(body)
    if status == "exists":
        raise HTTPException(status_code=409, detail="Column already exists")
    assert col is not None
    return col


@router.patch("/{column_id}", status_code=204, response_class=Response)
async def admin_update_column(
    column_id: str,
    body: ProjectsColumnUpdate,
    _: User = Depends(require_roles("moderator", "admin")),
    service: ProjectsService = Depends(get_projects_service),
) -> Response:
    st = await service.admin_update_column(column_id, body)
    if st == "not_found":
        raise HTTPException(status_code=404, detail="Column not found")
    return Response(status_code=204)


@router.delete("/{column_id}", status_code=204, response_class=Response)
async def admin_delete_column(
    column_id: str,
    _: User = Depends(require_roles("moderator", "admin")),
    service: ProjectsService = Depends(get_projects_service),
) -> Response:
    st = await service.admin_delete_column(column_id)
    if st == "not_found":
        raise HTTPException(status_code=404, detail="Column not found")
    if st == "not_empty":
        raise HTTPException(status_code=409, detail="Column is not empty")
    return Response(status_code=204)

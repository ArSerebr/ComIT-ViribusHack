"""Projects HTTP adapter: thin router → service only. No DB/repo access."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.modules.projects.deps import get_projects_service
from app.modules.projects.schemas import JoinRequest, JoinResponse
from app.modules.projects.service import ProjectsService

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("/hub")
async def get_projects_hub(service: ProjectsService = Depends(get_projects_service)):
    return await service.get_hub()


@router.get("/{project_id}")
async def get_project_by_id(
    project_id: str,
    service: ProjectsService = Depends(get_projects_service),
):
    details = await service.get_project_details(project_id)
    if details is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return details


@router.post("/{project_id}/join", response_model=JoinResponse)
async def post_project_join(
    project_id: str,
    body: JoinRequest = JoinRequest(),
    service: ProjectsService = Depends(get_projects_service),
) -> JoinResponse:
    ok = await service.join_project(project_id, body.message)
    if not ok:
        raise HTTPException(status_code=404, detail="Project not found")
    return JoinResponse(ok=True, project_id=project_id)

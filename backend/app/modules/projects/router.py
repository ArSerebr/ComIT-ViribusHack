"""Projects HTTP adapter: thin router → service only. No DB/repo access."""

from __future__ import annotations

from app.modules.auth.deps import current_active_user
from app.modules.auth.models import User
from app.modules.projects.deps import get_projects_service
from app.modules.projects.schemas import (
    JoinRequest,
    JoinResponse,
    ProjectCreateBody,
    ProjectUpdateBody,
    WorkPlanAssignBody,
    WorkPlanGenerateBody,
    WorkPlanGenerateResponse,
)
from app.modules.projects.service import ProjectsService
from fastapi import APIRouter, Depends, HTTPException, Response
from schemas import ErrorDetail, ProjectColumn, ProjectDetails

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post(
    "",
    response_model=ProjectDetails,
    responses={
        404: {"description": "Колонка не найдена", "model": ErrorDetail},
    },
)
async def create_project(
    body: ProjectCreateBody,
    user: User = Depends(current_active_user),
    service: ProjectsService = Depends(get_projects_service),
) -> ProjectDetails:
    status, details = await service.create_project(user, body)
    if status == "no_column":
        raise HTTPException(status_code=404, detail="Column not found")
    assert details is not None
    return details


@router.get("/hub", response_model=list[ProjectColumn])
async def get_projects_hub(service: ProjectsService = Depends(get_projects_service)):
    return await service.get_hub()


@router.patch(
    "/{project_id}",
    response_model=ProjectDetails,
    responses={
        404: {"description": "Проект не найден", "model": ErrorDetail},
        403: {"description": "Нет прав", "model": ErrorDetail},
    },
)
async def patch_project(
    project_id: str,
    body: ProjectUpdateBody,
    user: User = Depends(current_active_user),
    service: ProjectsService = Depends(get_projects_service),
) -> ProjectDetails:
    status, details = await service.update_project(user, project_id, body)
    if status == "not_found":
        raise HTTPException(status_code=404, detail="Project not found")
    if status == "forbidden":
        raise HTTPException(status_code=403, detail="Forbidden")
    assert details is not None
    return details


@router.delete(
    "/{project_id}",
    status_code=204,
    response_class=Response,
    responses={
        404: {"description": "Проект не найден", "model": ErrorDetail},
        403: {"description": "Нет прав", "model": ErrorDetail},
    },
)
async def delete_project(
    project_id: str,
    user: User = Depends(current_active_user),
    service: ProjectsService = Depends(get_projects_service),
) -> Response:
    st = await service.delete_project(user, project_id)
    if st == "not_found":
        raise HTTPException(status_code=404, detail="Project not found")
    if st == "forbidden":
        raise HTTPException(status_code=403, detail="Forbidden")
    return Response(status_code=204)


@router.get(
    "/{project_id}",
    response_model=ProjectDetails,
    responses={404: {"description": "Проект не найден", "model": ErrorDetail}},
)
async def get_project_by_id(
    project_id: str,
    service: ProjectsService = Depends(get_projects_service),
):
    details = await service.get_project_details(project_id)
    if details is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return details


@router.post(
    "/{project_id}/join",
    response_model=JoinResponse,
    responses={404: {"description": "Проект не найден", "model": ErrorDetail}},
)
async def post_project_join(
    project_id: str,
    body: JoinRequest = JoinRequest(),
    user: User = Depends(current_active_user),
    service: ProjectsService = Depends(get_projects_service),
) -> JoinResponse:
    ok = await service.join_project(user, project_id, body.message)
    if not ok:
        raise HTTPException(status_code=404, detail="Project not found")
    return JoinResponse(ok=True, project_id=project_id)


@router.post(
    "/{project_id}/work-plan/generate",
    response_model=WorkPlanGenerateResponse,
    responses={
        404: {"description": "Проект не найден", "model": ErrorDetail},
        403: {"description": "Нет прав", "model": ErrorDetail},
        503: {"description": "PulseCore не настроен", "model": ErrorDetail},
    },
)
async def post_work_plan_generate(
    project_id: str,
    body: WorkPlanGenerateBody = WorkPlanGenerateBody(),
    user: User = Depends(current_active_user),
    service: ProjectsService = Depends(get_projects_service),
) -> WorkPlanGenerateResponse:
    status, task_id = await service.start_work_plan_generate(
        user, project_id, body.project_deadline
    )
    if status == "not_found":
        raise HTTPException(status_code=404, detail="Project not found")
    if status == "forbidden":
        raise HTTPException(status_code=403, detail="Forbidden")
    if status == "misconfigured" or not task_id:
        raise HTTPException(status_code=503, detail="PulseCore client not configured")
    return WorkPlanGenerateResponse(task_id=task_id)


@router.post(
    "/{project_id}/work-plan/assign",
    responses={
        404: {"description": "Проект не найден", "model": ErrorDetail},
        403: {"description": "Нет прав", "model": ErrorDetail},
        400: {"description": "Некорректное тело", "model": ErrorDetail},
    },
)
async def post_work_plan_assign(
    project_id: str,
    body: WorkPlanAssignBody,
    user: User = Depends(current_active_user),
    service: ProjectsService = Depends(get_projects_service),
) -> dict:
    status, payload = await service.assign_work_plan(user, project_id, body.tasks)
    if status == "not_found":
        raise HTTPException(status_code=404, detail="Project not found")
    if status == "forbidden":
        raise HTTPException(status_code=403, detail="Forbidden")
    if status == "bad_request":
        raise HTTPException(status_code=400, detail="Invalid tasks or team")
    assert payload is not None
    return payload

from __future__ import annotations

from collections import defaultdict
from typing import Any, Literal, cast

from app.contracts.analytics import JoinRequestSink
from app.modules.projects.models import ProjectsProject, ProjectsProjectDetail
from app.modules.projects.repository import ProjectsRepository
from schemas import (
    HubProject,
    IntegrationItem,
    ParticipantRow,
    PersonPreview,
    ProductivityBlock,
    ProjectColumn,
    ProjectDetails,
    ProgressBlock,
    TodoBlock,
)


def _hub_project_from_orm(p: ProjectsProject) -> HubProject:
    vis: Literal["public", "private"] | None
    if p.visibility in ("public", "private"):
        vis = cast(Literal["public", "private"], p.visibility)
    else:
        vis = None
    return HubProject(
        id=p.id,
        code=p.code,
        title=p.title,
        description=p.description,
        teamName=p.team_name,
        updatedLabel=p.updated_label,
        teamAvatarUrl=p.team_avatar_url,
        detailsUrl=p.details_url,
        visibility=vis,
        isHot=p.is_hot,
    )


def _project_details_from_orm(project: ProjectsProject, detail: ProjectsProjectDetail) -> ProjectDetails:
    blocks: dict[str, Any] = detail.detail_blocks or {}
    team_raw = blocks.get("teamMembersPreview", [])
    prod_raw = blocks.get("productivity")
    prog_raw = blocks.get("progress")
    todo_raw = blocks.get("todo")
    int_raw = blocks.get("integrations", [])
    part_raw = blocks.get("participants", [])

    if not isinstance(prod_raw, dict) or not isinstance(prog_raw, dict) or not isinstance(todo_raw, dict):
        raise ValueError("Invalid project detail_blocks")

    return ProjectDetails(
        id=project.id,
        code=project.code,
        title=project.title,
        ownerName=detail.owner_name,
        detailsUrl=project.details_url,
        joinLabel=detail.join_label,
        teamCaption=detail.team_caption,
        productivityCaption=detail.productivity_caption,
        progressCaption=detail.progress_caption,
        todoCaption=detail.todo_caption,
        integrationCaption=detail.integration_caption,
        teamMembersPreview=[PersonPreview.model_validate(x) for x in team_raw],
        productivity=ProductivityBlock.model_validate(prod_raw),
        progress=ProgressBlock.model_validate(prog_raw),
        todo=TodoBlock.model_validate(todo_raw),
        integrations=[IntegrationItem.model_validate(x) for x in int_raw],
        participants=[ParticipantRow.model_validate(x) for x in part_raw],
    )


class ProjectsService:
    def __init__(self, repo: ProjectsRepository, join_sink: JoinRequestSink) -> None:
        self._repo = repo
        self._join_sink = join_sink

    async def get_hub(self) -> list[ProjectColumn]:
        columns = await self._repo.list_columns_ordered()
        projects = await self._repo.list_projects_ordered()
        by_col: dict[str, list[ProjectsProject]] = defaultdict(list)
        for p in projects:
            by_col[p.column_id].append(p)
        out: list[ProjectColumn] = []
        for col in columns:
            hubs = [_hub_project_from_orm(p) for p in by_col.get(col.id, [])]
            out.append(ProjectColumn(id=col.id, title=col.title, count=len(hubs), projects=hubs))
        return out

    async def get_project_details(self, project_id: str) -> ProjectDetails | None:
        row = await self._repo.get_project_and_detail(project_id)
        if row is None:
            return None
        project, detail = row
        if detail is None:
            return None
        try:
            return _project_details_from_orm(project, detail)
        except (ValueError, TypeError):
            return None

    async def join_project(self, project_id: str, message: str | None) -> bool:
        if not await self._repo.project_exists(project_id):
            return False
        await self._join_sink.record_join_request(project_id, message)
        return True

from __future__ import annotations

from collections import defaultdict
from typing import Any, Literal, cast

from app.contracts.analytics import JoinRequestSink
from app.core.permissions import can_edit_content
from app.modules.auth.models import User
from app.modules.projects.models import ProjectsColumn, ProjectsProject, ProjectsProjectDetail
from app.modules.projects.repository import ProjectsRepository
from app.modules.projects.schemas import (
    ProjectCreateBody,
    ProjectsColumnCreate,
    ProjectsColumnUpdate,
    ProjectUpdateBody,
)
from schemas import (
    HubProject,
    IntegrationItem,
    ParticipantRow,
    PersonPreview,
    ProductivityBlock,
    ProgressBlock,
    ProjectColumn,
    ProjectDetails,
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


def _project_details_from_orm(
    project: ProjectsProject, detail: ProjectsProjectDetail
) -> ProjectDetails:
    blocks: dict[str, Any] = detail.detail_blocks or {}
    team_raw = blocks.get("teamMembersPreview", [])
    prod_raw = blocks.get("productivity")
    prog_raw = blocks.get("progress")
    todo_raw = blocks.get("todo")
    int_raw = blocks.get("integrations", [])
    part_raw = blocks.get("participants", [])

    if (
        not isinstance(prod_raw, dict)
        or not isinstance(prog_raw, dict)
        or not isinstance(todo_raw, dict)
    ):
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

    def _blocks_from_create(self, body: ProjectCreateBody) -> dict[str, Any]:
        return {
            "teamMembersPreview": [p.model_dump() for p in body.team_members_preview],
            "productivity": body.productivity.model_dump(),
            "progress": body.progress.model_dump(),
            "todo": body.todo.model_dump(),
            "integrations": [i.model_dump() for i in body.integrations],
            "participants": [p.model_dump() for p in body.participants],
        }

    async def create_project(
        self,
        user: User,
        body: ProjectCreateBody,
    ) -> tuple[Literal["ok", "no_column", "exists"], ProjectDetails | None]:
        if await self._repo.project_exists(body.id):
            return ("exists", None)
        if not await self._repo.column_exists(body.column_id):
            return ("no_column", None)
        sort_order = await self._repo.max_sort_order_in_column(body.column_id) + 1
        vis = body.visibility
        project = ProjectsProject(
            id=body.id,
            code=body.code,
            title=body.title,
            description=body.description,
            team_name=body.team_name,
            updated_label=body.updated_label,
            team_avatar_url=body.team_avatar_url,
            details_url=body.details_url,
            visibility=vis,
            is_hot=body.is_hot,
            column_id=body.column_id,
            sort_order=sort_order,
            owner_user_id=user.id,
        )
        detail = ProjectsProjectDetail(
            project_id=body.id,
            owner_name=body.owner_name,
            join_label=body.join_label,
            team_caption=body.team_caption,
            productivity_caption=body.productivity_caption,
            progress_caption=body.progress_caption,
            todo_caption=body.todo_caption,
            integration_caption=body.integration_caption,
            detail_blocks=self._blocks_from_create(body),
        )
        await self._repo.add_project(project)
        await self._repo.add_detail(detail)
        return ("ok", _project_details_from_orm(project, detail))

    async def update_project(
        self,
        user: User,
        project_id: str,
        body: ProjectUpdateBody,
    ) -> tuple[Literal["ok", "not_found", "forbidden"], ProjectDetails | None]:
        row = await self._repo.get_project_and_detail(project_id)
        if row is None:
            return ("not_found", None)
        project, detail = row
        if detail is None:
            return ("not_found", None)
        if not can_edit_content(user, project.owner_user_id):
            return ("forbidden", None)
        data = body.model_dump(exclude_unset=True, by_alias=False)
        if "column_id" in data and data["column_id"] is not None:
            cid = data["column_id"]
            if not await self._repo.column_exists(cid):
                return ("not_found", None)
            project.column_id = cid
        if "code" in data and data["code"] is not None:
            project.code = data["code"]
        if "title" in data and data["title"] is not None:
            project.title = data["title"]
        if "description" in data and data["description"] is not None:
            project.description = data["description"]
        if "team_name" in data and data["team_name"] is not None:
            project.team_name = data["team_name"]
        if "updated_label" in data and data["updated_label"] is not None:
            project.updated_label = data["updated_label"]
        if "team_avatar_url" in data and data["team_avatar_url"] is not None:
            project.team_avatar_url = data["team_avatar_url"]
        if "details_url" in data and data["details_url"] is not None:
            project.details_url = data["details_url"]
        if "visibility" in data:
            project.visibility = data["visibility"]
        if "is_hot" in data:
            project.is_hot = data["is_hot"]

        blocks: dict[str, Any] = dict(detail.detail_blocks or {})
        if "owner_name" in data and data["owner_name"] is not None:
            detail.owner_name = data["owner_name"]
        if "join_label" in data and data["join_label"] is not None:
            detail.join_label = data["join_label"]
        if "team_caption" in data and data["team_caption"] is not None:
            detail.team_caption = data["team_caption"]
        if "productivity_caption" in data and data["productivity_caption"] is not None:
            detail.productivity_caption = data["productivity_caption"]
        if "progress_caption" in data and data["progress_caption"] is not None:
            detail.progress_caption = data["progress_caption"]
        if "todo_caption" in data and data["todo_caption"] is not None:
            detail.todo_caption = data["todo_caption"]
        if "integration_caption" in data and data["integration_caption"] is not None:
            detail.integration_caption = data["integration_caption"]
        if body.team_members_preview is not None:
            blocks["teamMembersPreview"] = [p.model_dump() for p in body.team_members_preview]
        if body.productivity is not None:
            blocks["productivity"] = body.productivity.model_dump()
        if body.progress is not None:
            blocks["progress"] = body.progress.model_dump()
        if body.todo is not None:
            blocks["todo"] = body.todo.model_dump()
        if body.integrations is not None:
            blocks["integrations"] = [i.model_dump() for i in body.integrations]
        if body.participants is not None:
            blocks["participants"] = [p.model_dump() for p in body.participants]
        detail.detail_blocks = blocks
        try:
            out = _project_details_from_orm(project, detail)
        except (ValueError, TypeError):
            return ("not_found", None)
        return ("ok", out)

    async def delete_project(
        self,
        user: User,
        project_id: str,
    ) -> Literal["ok", "not_found", "forbidden"]:
        project = await self._repo.get_project_only(project_id)
        if project is None:
            return "not_found"
        if not can_edit_content(user, project.owner_user_id):
            return "forbidden"
        await self._repo.delete_project(project_id)
        return "ok"

    async def admin_create_column(
        self,
        body: ProjectsColumnCreate,
    ) -> tuple[Literal["ok", "exists"], ProjectColumn | None]:
        if await self._repo.get_column(body.id) is not None:
            return ("exists", None)
        so = await self._repo.max_column_sort_order() + 1
        col = ProjectsColumn(id=body.id, title=body.title, sort_order=so)
        await self._repo.add_column(col)
        return ("ok", ProjectColumn(id=col.id, title=col.title, count=0, projects=[]))

    async def admin_update_column(
        self,
        column_id: str,
        body: ProjectsColumnUpdate,
    ) -> Literal["ok", "not_found"]:
        col = await self._repo.get_column(column_id)
        if col is None:
            return "not_found"
        if body.title is not None:
            col.title = body.title
        if body.sort_order is not None:
            col.sort_order = body.sort_order
        return "ok"

    async def admin_delete_column(self, column_id: str) -> Literal["ok", "not_found", "not_empty"]:
        if await self._repo.get_column(column_id) is None:
            return "not_found"
        if await self._repo.count_projects_in_column(column_id) > 0:
            return "not_empty"
        await self._repo.delete_column(column_id)
        return "ok"

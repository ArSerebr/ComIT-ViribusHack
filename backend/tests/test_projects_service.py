"""ProjectsService: сборка hub-колонок и join без реальной БД."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.modules.projects.models import ProjectsColumn, ProjectsProject
from app.modules.projects.schemas import ProjectCreateBody, ProjectUpdateBody
from app.modules.projects.service import ProjectsService
from schemas import (
    IntegrationItem,
    ParticipantRow,
    ProductivityBlock,
    ProgressBlock,
    TodoBlock,
)


def _project(pid: str, col_id: str) -> ProjectsProject:
    p = MagicMock(spec=ProjectsProject)
    p.id = pid
    p.code = "C"
    p.title = "T"
    p.description = "D"
    p.team_name = "Team"
    p.updated_label = "now"
    p.team_avatar_url = "https://x/a.png"
    p.details_url = "https://x/p"
    p.visibility = "public"
    p.is_hot = False
    p.column_id = col_id
    return p


@pytest.mark.asyncio
async def test_get_hub_groups_projects_by_column():
    repo = AsyncMock()
    c1 = MagicMock(spec=ProjectsColumn)
    c1.id = "col-a"
    c1.title = "Column A"
    c2 = MagicMock(spec=ProjectsColumn)
    c2.id = "col-b"
    c2.title = "Column B"
    repo.list_columns_ordered = AsyncMock(return_value=[c1, c2])
    repo.list_projects_ordered = AsyncMock(
        return_value=[
            _project("p1", "col-a"),
            _project("p2", "col-a"),
            _project("p3", "col-b"),
        ],
    )
    sink = AsyncMock()
    svc = ProjectsService(repo, sink)

    columns = await svc.get_hub()

    assert len(columns) == 2
    assert columns[0].id == "col-a"
    assert columns[0].count == 2
    assert columns[0].projects[0].id == "p1"
    assert columns[1].id == "col-b"
    assert columns[1].count == 1


@pytest.mark.asyncio
async def test_join_project_records_when_exists():
    repo = AsyncMock()
    repo.project_exists = AsyncMock(return_value=True)
    sink = AsyncMock()
    svc = ProjectsService(repo, sink)
    uid = uuid.uuid4()
    user = MagicMock()
    user.id = uid

    ok = await svc.join_project(user, "proj-1", "hello")

    assert ok is True
    sink.record_join_request.assert_awaited_once_with("proj-1", "hello", uid)


@pytest.mark.asyncio
async def test_join_project_false_when_missing():
    repo = AsyncMock()
    repo.project_exists = AsyncMock(return_value=False)
    sink = AsyncMock()
    svc = ProjectsService(repo, sink)
    user = MagicMock()
    user.id = uuid.uuid4()

    ok = await svc.join_project(user, "missing", None)

    assert ok is False
    sink.record_join_request.assert_not_awaited()


def _minimal_create_body(pid: str, column_id: str) -> ProjectCreateBody:
    return ProjectCreateBody(
        id=pid,
        column_id=column_id,
        code="#X",
        title="T",
        description="D",
        team_name="Team",
        updated_label="now",
        team_avatar_url="https://x/a.png",
        details_url="/p",
        owner_name="Owner",
        join_label="Join",
        team_caption="TC",
        productivity_caption="PC",
        progress_caption="PrC",
        todo_caption="TodoC",
        integration_caption="IC",
        team_members_preview=[],
        productivity=ProductivityBlock(value="0%", delta="0"),
        progress=ProgressBlock(value="0%", percent=0),
        todo=TodoBlock(task="t", updatedLabel="u"),
        integrations=[
            IntegrationItem(
                id="i1",
                brand="b",
                description="d",
                statusLabel="s",
                connectedSince="c",
            )
        ],
        participants=[],
    )


@pytest.mark.asyncio
async def test_create_project_ok():
    repo = AsyncMock()
    repo.project_exists = AsyncMock(return_value=False)
    repo.column_exists = AsyncMock(return_value=True)
    repo.max_sort_order_in_column = AsyncMock(return_value=-1)
    repo.add_project = AsyncMock()
    repo.add_detail = AsyncMock()
    sink = AsyncMock()
    uid = uuid.uuid4()
    user = MagicMock()
    user.id = uid
    user.role = "user"
    svc = ProjectsService(repo, sink)
    body = _minimal_create_body("new-proj", "col-a")
    status, details = await svc.create_project(user, body)
    assert status == "ok"
    assert details is not None
    assert details.id == "new-proj"
    proj = repo.add_project.call_args[0][0]
    assert proj.owner_user_id == uid


@pytest.mark.asyncio
async def test_create_project_transliterates_cyrillic_id():
    repo = AsyncMock()
    repo.project_exists = AsyncMock(return_value=False)
    repo.column_exists = AsyncMock(return_value=True)
    repo.max_sort_order_in_column = AsyncMock(return_value=-1)
    repo.add_project = AsyncMock()
    repo.add_detail = AsyncMock()
    sink = AsyncMock()
    uid = uuid.uuid4()
    user = MagicMock()
    user.id = uid
    user.role = "user"
    svc = ProjectsService(repo, sink)
    body = _minimal_create_body("сырок-r110", "col-a")
    status, details = await svc.create_project(user, body)
    assert status == "ok"
    assert details is not None
    assert details.id == "syrok-r110"
    assert details.detailsUrl == "/projects/syrok-r110"
    proj = repo.add_project.call_args[0][0]
    assert proj.id == "syrok-r110"
    assert proj.details_url == "/projects/syrok-r110"


@pytest.mark.asyncio
async def test_delete_project_forbidden_for_stranger():
    owner = uuid.uuid4()
    p = MagicMock(spec=ProjectsProject)
    p.id = "p1"
    p.owner_user_id = owner
    p.group_chat_id = None
    repo = AsyncMock()
    repo.get_project_only = AsyncMock(return_value=p)
    sink = AsyncMock()
    svc = ProjectsService(repo, sink)
    user = MagicMock()
    user.id = uuid.uuid4()
    user.role = "user"
    st = await svc.delete_project(user, "p1")
    assert st == "forbidden"
    repo.delete_project.assert_not_called()


@pytest.mark.asyncio
async def test_update_project_moderator_can_edit_system_project():
    owner_row = MagicMock(spec=ProjectsProject)
    owner_row.id = "p1"
    owner_row.code = "c"
    owner_row.title = "t"
    owner_row.description = "d"
    owner_row.team_name = "tn"
    owner_row.updated_label = "u"
    owner_row.team_avatar_url = "https://x"
    owner_row.details_url = "https://d"
    owner_row.visibility = None
    owner_row.is_hot = None
    owner_row.column_id = "col"
    owner_row.owner_user_id = None
    owner_row.group_chat_id = None
    detail = MagicMock()
    detail.owner_name = "o"
    detail.join_label = "j"
    detail.team_caption = "tc"
    detail.productivity_caption = "pc"
    detail.progress_caption = "prc"
    detail.todo_caption = "tc2"
    detail.integration_caption = "ic"
    detail.detail_blocks = {
        "teamMembersPreview": [],
        "productivity": {"value": "1%", "delta": "0"},
        "progress": {"value": "1%", "percent": 1},
        "todo": {"task": "x", "updatedLabel": "y"},
        "integrations": [],
        "participants": [],
    }
    repo = AsyncMock()
    repo.get_project_and_detail = AsyncMock(return_value=(owner_row, detail))
    repo.column_exists = AsyncMock(return_value=True)
    sink = AsyncMock()
    user = MagicMock()
    user.id = uuid.uuid4()
    user.role = "moderator"
    svc = ProjectsService(repo, sink)
    status, out = await svc.update_project(user, "p1", ProjectUpdateBody(title="New"))
    assert status == "ok"
    assert out is not None
    assert owner_row.title == "New"


@pytest.mark.asyncio
async def test_start_work_plan_generate_ok():
    uid = uuid.uuid4()
    user = MagicMock()
    user.id = uid
    project = MagicMock(spec=ProjectsProject)
    project.id = "p1"
    project.owner_user_id = uid
    project.description = "D"
    repo = AsyncMock()
    repo.get_project_only = AsyncMock(return_value=project)
    pulse = AsyncMock()
    pulse.submit_work_plan = AsyncMock(return_value="task-abc")
    sink = AsyncMock()
    svc = ProjectsService(repo, sink, pulse)
    details = MagicMock()
    details.title = "Title"
    details.description = "D"
    details.participants = []
    with patch.object(svc, "get_project_details", new_callable=AsyncMock, return_value=details):
        st, tid = await svc.start_work_plan_generate(user, "p1", "2026-06-01")
    assert st == "ok"
    assert tid == "task-abc"
    pulse.submit_work_plan.assert_awaited_once()


@pytest.mark.asyncio
async def test_start_work_plan_generate_misconfigured_without_pulse():
    uid = uuid.uuid4()
    user = MagicMock()
    user.id = uid
    repo = AsyncMock()
    sink = AsyncMock()
    svc = ProjectsService(repo, sink, None)
    st, tid = await svc.start_work_plan_generate(user, "p1", None)
    assert st == "misconfigured"
    assert tid is None


@pytest.mark.asyncio
async def test_assign_work_plan_delegates_to_task_model():
    uid = uuid.uuid4()
    user = MagicMock()
    user.id = uid
    project = MagicMock(spec=ProjectsProject)
    project.id = "p1"
    project.title = "T"
    project.description = "D"
    project.owner_user_id = uid
    repo = AsyncMock()
    repo.get_project_only = AsyncMock(return_value=project)
    sink = AsyncMock()
    svc = ProjectsService(repo, sink, None)
    details = MagicMock()
    details.participants = [
        ParticipantRow(
            id="m1",
            name="Member",
            avatarUrl="",
            avatarVariant="default",
            role="Backend Engineer",
            skills=["python"],
        )
    ]
    task = {
        "id": "t1",
        "title": "Implement API",
        "description": "REST",
        "required_skills": ["python"],
        "category": "backend",
        "difficulty": "medium",
        "estimated_hours": 8,
        "priority": "must_have",
        "deadline_iso": "2026-05-01",
    }
    with patch.object(svc, "get_project_details", new_callable=AsyncMock, return_value=details):
        with patch("app.modules.projects.service.TaskAssignmentModel") as TM:
            TM.return_value.assign_project_data.return_value = {"project_id": "p1", "assignments": []}
            st, payload = await svc.assign_work_plan(user, "p1", [task])
    assert st == "ok"
    assert payload == {"project_id": "p1", "assignments": []}
    TM.return_value.assign_project_data.assert_called_once()

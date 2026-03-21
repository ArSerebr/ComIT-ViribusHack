"""ProjectsService: сборка hub-колонок и join без реальной БД."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.projects.models import ProjectsColumn, ProjectsProject
from app.modules.projects.service import ProjectsService


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

    ok = await svc.join_project("proj-1", "hello")

    assert ok is True
    sink.record_join_request.assert_awaited_once_with("proj-1", "hello")


@pytest.mark.asyncio
async def test_join_project_false_when_missing():
    repo = AsyncMock()
    repo.project_exists = AsyncMock(return_value=False)
    sink = AsyncMock()
    svc = ProjectsService(repo, sink)

    ok = await svc.join_project("missing", None)

    assert ok is False
    sink.record_join_request.assert_not_awaited()

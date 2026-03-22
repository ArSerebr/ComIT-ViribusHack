from __future__ import annotations

import uuid
from collections.abc import Sequence

from app.contracts.projects import ProjectQueryPort
from app.modules.projects.repository import ProjectsRepository
from sqlalchemy.ext.asyncio import AsyncSession


async def get_projects_by_owner_ids(
    session: AsyncSession, owner_ids: Sequence[uuid.UUID]
) -> list[tuple[str, str, uuid.UUID | None]]:
    """Return (id, title, owner_user_id) for projects owned by given users."""
    repo = ProjectsRepository(session)
    return await repo.get_projects_by_owner_ids(owner_ids)


class _ProjectQuery(ProjectQueryPort):
    def __init__(self, repo: ProjectsRepository) -> None:
        self._repo = repo

    async def project_exists(self, project_id: str) -> bool:
        return await self._repo.project_exists(project_id)


def create_project_query_port(session: AsyncSession) -> ProjectQueryPort:
    return _ProjectQuery(ProjectsRepository(session))

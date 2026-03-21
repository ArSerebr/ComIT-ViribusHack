from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.projects import ProjectQueryPort
from app.modules.projects.repository import ProjectsRepository


class _ProjectQuery(ProjectQueryPort):
    def __init__(self, repo: ProjectsRepository) -> None:
        self._repo = repo

    async def project_exists(self, project_id: str) -> bool:
        return await self._repo.project_exists(project_id)


def create_project_query_port(session: AsyncSession) -> ProjectQueryPort:
    return _ProjectQuery(ProjectsRepository(session))

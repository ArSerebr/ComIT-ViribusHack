from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.projects.models import ProjectsColumn, ProjectsProject, ProjectsProjectDetail


class ProjectsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def project_exists(self, project_id: str) -> bool:
        stmt = select(ProjectsProject.id).where(ProjectsProject.id == project_id).limit(1)
        r = await self._session.execute(stmt)
        return r.scalar_one_or_none() is not None

    async def list_columns_ordered(self) -> list[ProjectsColumn]:
        stmt = select(ProjectsColumn).order_by(ProjectsColumn.sort_order, ProjectsColumn.id)
        return list((await self._session.execute(stmt)).scalars().all())

    async def list_projects_ordered(self) -> list[ProjectsProject]:
        stmt = select(ProjectsProject).order_by(
            ProjectsProject.column_id,
            ProjectsProject.sort_order,
            ProjectsProject.id,
        )
        return list((await self._session.execute(stmt)).scalars().all())

    async def get_project_and_detail(
        self,
        project_id: str,
    ) -> tuple[ProjectsProject, ProjectsProjectDetail | None] | None:
        stmt = select(ProjectsProject).where(ProjectsProject.id == project_id)
        project = (await self._session.execute(stmt)).scalar_one_or_none()
        if project is None:
            return None
        d_stmt = select(ProjectsProjectDetail).where(ProjectsProjectDetail.project_id == project_id)
        detail = (await self._session.execute(d_stmt)).scalar_one_or_none()
        return (project, detail)

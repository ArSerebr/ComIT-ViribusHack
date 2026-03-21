from __future__ import annotations

from app.modules.projects.models import ProjectsColumn, ProjectsProject, ProjectsProjectDetail
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession


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

    async def get_project_only(self, project_id: str) -> ProjectsProject | None:
        stmt = select(ProjectsProject).where(ProjectsProject.id == project_id)
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def column_exists(self, column_id: str) -> bool:
        stmt = select(ProjectsColumn.id).where(ProjectsColumn.id == column_id).limit(1)
        return (await self._session.execute(stmt)).scalar_one_or_none() is not None

    async def max_sort_order_in_column(self, column_id: str) -> int:
        stmt = select(func.coalesce(func.max(ProjectsProject.sort_order), -1)).where(
            ProjectsProject.column_id == column_id
        )
        v = (await self._session.execute(stmt)).scalar_one()
        return int(v) if v is not None else -1

    async def count_projects_in_column(self, column_id: str) -> int:
        stmt = (
            select(func.count())
            .select_from(ProjectsProject)
            .where(ProjectsProject.column_id == column_id)
        )
        return int((await self._session.execute(stmt)).scalar_one() or 0)

    async def add_project(self, row: ProjectsProject) -> None:
        self._session.add(row)

    async def add_detail(self, row: ProjectsProjectDetail) -> None:
        self._session.add(row)

    async def commit(self) -> None:
        await self._session.commit()

    async def delete_project(self, project_id: str) -> bool:
        res = await self._session.execute(
            delete(ProjectsProject).where(ProjectsProject.id == project_id)
        )
        return (res.rowcount or 0) > 0

    async def get_column(self, column_id: str) -> ProjectsColumn | None:
        stmt = select(ProjectsColumn).where(ProjectsColumn.id == column_id)
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def add_column(self, row: ProjectsColumn) -> None:
        self._session.add(row)

    async def delete_column(self, column_id: str) -> bool:
        res = await self._session.execute(
            delete(ProjectsColumn).where(ProjectsColumn.id == column_id)
        )
        return (res.rowcount or 0) > 0

    async def max_column_sort_order(self) -> int:
        stmt = select(func.coalesce(func.max(ProjectsColumn.sort_order), -1))
        v = (await self._session.execute(stmt)).scalar_one()
        return int(v) if v is not None else -1

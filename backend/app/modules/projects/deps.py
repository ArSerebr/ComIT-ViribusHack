from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.modules.analytics.public_api import create_join_request_sink
from app.modules.projects.repository import ProjectsRepository
from app.modules.projects.service import ProjectsService


async def get_projects_service(
    session: AsyncSession = Depends(get_db),
) -> ProjectsService:
    return ProjectsService(ProjectsRepository(session), create_join_request_sink(session))

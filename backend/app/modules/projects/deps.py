from __future__ import annotations

from app.core.db.session import get_db
from app.modules.analytics.public_api import create_join_request_sink
from app.modules.pulse.client import PulseCoreClient
from app.modules.pulse.deps import get_pulse_client
from app.modules.projects.repository import ProjectsRepository
from app.modules.projects.service import ProjectsService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_projects_service(
    session: AsyncSession = Depends(get_db),
    pulse_client: PulseCoreClient = Depends(get_pulse_client),
) -> ProjectsService:
    return ProjectsService(
        ProjectsRepository(session),
        create_join_request_sink(session),
        pulse_client,
    )

from __future__ import annotations

from app.core.db.session import get_db
from app.modules.dashboard.repository import DashboardRepository
from app.modules.dashboard.service import DashboardService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_dashboard_service(session: AsyncSession = Depends(get_db)) -> DashboardService:
    return DashboardService(DashboardRepository(session))

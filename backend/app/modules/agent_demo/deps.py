"""Зависимости модуля agent_demo."""

from __future__ import annotations

from app.core.db.session import get_db
from app.modules.agent_demo.repository import AgentDemoRepository
from app.modules.agent_demo.service import AgentDemoService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


def get_agent_demo_service(
    session: AsyncSession = Depends(get_db),
) -> AgentDemoService:
    return AgentDemoService(AgentDemoRepository(session))

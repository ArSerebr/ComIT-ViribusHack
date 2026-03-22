from __future__ import annotations

from app.core.db.session import get_db
from app.modules.hackathons.repository import HackathonRepository
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


def get_hackathon_repository(
    session: AsyncSession = Depends(get_db),
) -> HackathonRepository:
    return HackathonRepository(session)

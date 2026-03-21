from __future__ import annotations

from app.core.db.session import get_db
from app.modules.library.public_api import create_interest_catalog_port
from app.modules.profile.repository import ProfileRepository
from app.modules.profile.service import ProfileService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_profile_service(session: AsyncSession = Depends(get_db)) -> ProfileService:
    interest_catalog = create_interest_catalog_port(session)
    return ProfileService(session, ProfileRepository(session), interest_catalog)

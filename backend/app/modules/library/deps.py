from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.modules.library.repository import LibraryRepository
from app.modules.library.service import LibraryService


async def get_library_service(session: AsyncSession = Depends(get_db)) -> LibraryService:
    return LibraryService(LibraryRepository(session))

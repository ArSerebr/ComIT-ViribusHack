from __future__ import annotations

from app.contracts.library import InterestCatalogPort
from app.core.db.session import get_db
from app.modules.library.public_api import create_interest_catalog_port
from app.modules.library.repository import LibraryRepository
from app.modules.library.service import LibraryService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_library_service(session: AsyncSession = Depends(get_db)) -> LibraryService:
    return LibraryService(LibraryRepository(session))


async def get_interest_catalog_port(
    session: AsyncSession = Depends(get_db),
) -> InterestCatalogPort:
    return create_interest_catalog_port(session)

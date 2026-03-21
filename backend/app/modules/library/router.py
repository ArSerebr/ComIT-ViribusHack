"""Library HTTP adapter: thin router → service only. No DB/repo access."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.modules.library.deps import get_library_service
from app.modules.library.service import LibraryService

router = APIRouter(prefix="/api", tags=["library"])


@router.get("/library")
async def get_library(service: LibraryService = Depends(get_library_service)):
    return await service.get_bundle()

from __future__ import annotations

from collections.abc import Sequence

from app.contracts.library import InterestCatalogPort
from app.modules.library.repository import LibraryRepository
from sqlalchemy.ext.asyncio import AsyncSession


class _InterestCatalog(InterestCatalogPort):
    def __init__(self, repo: LibraryRepository) -> None:
        self._repo = repo

    async def all_interest_option_ids_exist(self, interest_ids: Sequence[str]) -> bool:
        return await self._repo.all_interest_option_ids_exist(interest_ids)

    async def labels_for_interest_ids(self, interest_ids: Sequence[str]) -> dict[str, str]:
        return await self._repo.labels_for_interest_ids(interest_ids)


def create_interest_catalog_port(session: AsyncSession) -> InterestCatalogPort:
    return _InterestCatalog(LibraryRepository(session))

from __future__ import annotations

import uuid
from collections.abc import Sequence

from app.contracts.library import InterestCatalogPort
from app.modules.library.repository import LibraryRepository
from sqlalchemy.ext.asyncio import AsyncSession


async def get_articles_by_owner_ids(
    session: AsyncSession, owner_ids: Sequence[uuid.UUID]
) -> list[tuple[str, str, str, uuid.UUID | None]]:
    """Return (id, title, author_name, owner_user_id) for articles owned by given users."""
    repo = LibraryRepository(session)
    return await repo.get_articles_by_owner_ids(owner_ids)


class _InterestCatalog(InterestCatalogPort):
    def __init__(self, repo: LibraryRepository) -> None:
        self._repo = repo

    async def all_interest_option_ids_exist(self, interest_ids: Sequence[str]) -> bool:
        return await self._repo.all_interest_option_ids_exist(interest_ids)

    async def labels_for_interest_ids(self, interest_ids: Sequence[str]) -> dict[str, str]:
        return await self._repo.labels_for_interest_ids(interest_ids)


def create_interest_catalog_port(session: AsyncSession) -> InterestCatalogPort:
    return _InterestCatalog(LibraryRepository(session))

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.library.models import (
    LibraryArticle,
    LibraryArticleTag,
    LibraryInterestOption,
    LibraryShowcaseItem,
    LibraryTag,
)


class LibraryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_showcase_ordered(self) -> list[LibraryShowcaseItem]:
        stmt = select(LibraryShowcaseItem).order_by(
            LibraryShowcaseItem.sort_order,
            LibraryShowcaseItem.id,
        )
        return list((await self._session.execute(stmt)).scalars().all())

    async def list_interests_ordered(self) -> list[LibraryInterestOption]:
        stmt = select(LibraryInterestOption).order_by(
            LibraryInterestOption.sort_order,
            LibraryInterestOption.id,
        )
        return list((await self._session.execute(stmt)).scalars().all())

    async def list_articles_ordered(self) -> list[LibraryArticle]:
        stmt = select(LibraryArticle).order_by(LibraryArticle.id)
        return list((await self._session.execute(stmt)).scalars().all())

    async def list_tags_for_article(self, article_id: str) -> list[LibraryTag]:
        stmt = (
            select(LibraryTag)
            .join(LibraryArticleTag, LibraryArticleTag.tag_id == LibraryTag.id)
            .where(LibraryArticleTag.article_id == article_id)
            .order_by(LibraryArticleTag.position, LibraryTag.id)
        )
        return list((await self._session.execute(stmt)).scalars().all())

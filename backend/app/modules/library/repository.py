from __future__ import annotations

import uuid
from collections.abc import Sequence

from app.modules.library.models import (
    LibraryArticle,
    LibraryArticleTag,
    LibraryInterestOption,
    LibraryInterestTag,
    LibraryShowcaseItem,
    LibraryTag,
)
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession


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

    async def all_interest_option_ids_exist(self, interest_ids: Sequence[str]) -> bool:
        unique = frozenset(interest_ids)
        if not unique:
            return True
        stmt = (
            select(func.count())
            .select_from(LibraryInterestOption)
            .where(LibraryInterestOption.id.in_(unique))
        )
        n = (await self._session.execute(stmt)).scalar_one()
        return int(n) == len(unique)

    async def labels_for_interest_ids(self, interest_ids: Sequence[str]) -> dict[str, str]:
        if not interest_ids:
            return {}
        stmt = select(LibraryInterestOption.id, LibraryInterestOption.label).where(
            LibraryInterestOption.id.in_(interest_ids)
        )
        rows = (await self._session.execute(stmt)).all()
        return {str(r[0]): str(r[1]) for r in rows}

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

    async def list_interest_ids_for_articles(self, article_ids: Sequence[str]) -> dict[str, list[str]]:
        """Interest option ids per article, derived from article tags and ``library_interest_tag``."""
        if not article_ids:
            return {}
        stmt = (
            select(LibraryArticleTag.article_id, LibraryInterestTag.interest_id)
            .join(LibraryInterestTag, LibraryInterestTag.tag_id == LibraryArticleTag.tag_id)
            .where(LibraryArticleTag.article_id.in_(article_ids))
        )
        rows = (await self._session.execute(stmt)).all()
        by_article: dict[str, set[str]] = {}
        for aid, iid in rows:
            by_article.setdefault(str(aid), set()).add(str(iid))
        return {aid: sorted(ids) for aid, ids in by_article.items()}

    async def get_article(self, article_id: str) -> LibraryArticle | None:
        stmt = select(LibraryArticle).where(LibraryArticle.id == article_id)
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def add_article(self, row: LibraryArticle) -> None:
        self._session.add(row)

    async def flush(self) -> None:
        await self._session.flush()

    async def commit(self) -> None:
        await self._session.commit()

    async def delete_article(self, article_id: str) -> bool:
        res = await self._session.execute(
            delete(LibraryArticle).where(LibraryArticle.id == article_id)
        )
        return (res.rowcount or 0) > 0

    async def all_tag_ids_exist(self, tag_ids: Sequence[str]) -> bool:
        unique = frozenset(tag_ids)
        if not unique:
            return True
        stmt = select(func.count()).select_from(LibraryTag).where(LibraryTag.id.in_(unique))
        n = (await self._session.execute(stmt)).scalar_one()
        return int(n) == len(unique)

    async def replace_article_tags(self, article_id: str, tag_ids: list[str]) -> None:
        await self._session.execute(
            delete(LibraryArticleTag).where(LibraryArticleTag.article_id == article_id)
        )
        for pos, tid in enumerate(tag_ids):
            self._session.add(
                LibraryArticleTag(article_id=article_id, tag_id=tid, position=pos),
            )

    async def get_showcase(self, item_id: str) -> LibraryShowcaseItem | None:
        stmt = select(LibraryShowcaseItem).where(LibraryShowcaseItem.id == item_id)
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def add_showcase(self, row: LibraryShowcaseItem) -> None:
        self._session.add(row)

    async def delete_showcase(self, item_id: str) -> bool:
        res = await self._session.execute(
            delete(LibraryShowcaseItem).where(LibraryShowcaseItem.id == item_id)
        )
        return (res.rowcount or 0) > 0

    async def max_showcase_sort_order(self) -> int:
        stmt = select(func.coalesce(func.max(LibraryShowcaseItem.sort_order), -1))
        v = (await self._session.execute(stmt)).scalar_one()
        return int(v) if v is not None else -1

    async def get_interest(self, interest_id: str) -> LibraryInterestOption | None:
        stmt = select(LibraryInterestOption).where(LibraryInterestOption.id == interest_id)
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def add_interest(self, row: LibraryInterestOption) -> None:
        self._session.add(row)

    async def delete_interest(self, interest_id: str) -> bool:
        res = await self._session.execute(
            delete(LibraryInterestOption).where(LibraryInterestOption.id == interest_id)
        )
        return (res.rowcount or 0) > 0

    async def max_interest_sort_order(self) -> int:
        stmt = select(func.coalesce(func.max(LibraryInterestOption.sort_order), -1))
        v = (await self._session.execute(stmt)).scalar_one()
        return int(v) if v is not None else -1

    async def get_tag(self, tag_id: str) -> LibraryTag | None:
        stmt = select(LibraryTag).where(LibraryTag.id == tag_id)
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def add_tag(self, row: LibraryTag) -> None:
        self._session.add(row)

    async def delete_tag(self, tag_id: str) -> bool:
        res = await self._session.execute(delete(LibraryTag).where(LibraryTag.id == tag_id))
        return (res.rowcount or 0) > 0

    async def article_references_tag(self, tag_id: str) -> bool:
        stmt = (
            select(LibraryArticleTag.article_id).where(LibraryArticleTag.tag_id == tag_id).limit(1)
        )
        return (await self._session.execute(stmt)).first() is not None

    async def get_articles_by_owner_ids(
        self, owner_ids: Sequence[uuid.UUID]
    ) -> list[tuple[str, str, str, uuid.UUID | None]]:
        """Return (id, title, author_name, owner_user_id) for articles owned by given users."""
        if not owner_ids:
            return []
        stmt = (
            select(
                LibraryArticle.id,
                LibraryArticle.title,
                LibraryArticle.author_name,
                LibraryArticle.owner_user_id,
            )
            .where(LibraryArticle.owner_user_id.in_(owner_ids))
            .order_by(LibraryArticle.owner_user_id, LibraryArticle.id)
        )
        rows = (await self._session.execute(stmt)).all()
        return [(r[0], r[1], r[2], r[3]) for r in rows]

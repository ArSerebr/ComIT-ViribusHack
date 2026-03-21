from __future__ import annotations

from typing import Literal

from app.core.permissions import can_edit_content, is_moderator_or_admin
from app.modules.auth.models import User
from app.modules.news.models import NewsFeatured, NewsMini
from app.modules.news.repository import NewsRepository
from app.modules.news.schemas import (
    NewsFeaturedCreateBody,
    NewsFeaturedUpdateBody,
    NewsMiniCreateBody,
    NewsMiniUpdateBody,
)
from schemas import FeaturedNewsItem, NewsMiniItem


def _mini_to_schema(row: NewsMini) -> NewsMiniItem:
    return NewsMiniItem(
        id=row.id,
        title=row.title,
        imageUrl=row.image_url,
        detailsUrl=row.details_url,
    )


def _featured_to_schema(row: NewsFeatured) -> FeaturedNewsItem:
    return FeaturedNewsItem(
        id=row.id,
        title=row.title,
        subtitle=row.subtitle,
        description=row.description,
        imageUrl=row.image_url,
        ctaLabel=row.cta_label,
        detailsUrl=row.details_url,
    )


class NewsService:
    def __init__(self, repo: NewsRepository) -> None:
        self._repo = repo

    async def list_mini(self) -> list[NewsMiniItem]:
        rows = await self._repo.list_mini_ordered()
        return [_mini_to_schema(r) for r in rows]

    async def list_featured(self) -> list[FeaturedNewsItem]:
        rows = await self._repo.list_featured_ordered()
        return [_featured_to_schema(r) for r in rows]

    async def create_news_mini(
        self,
        user: User,
        body: NewsMiniCreateBody,
    ) -> tuple[Literal["ok", "exists"], NewsMiniItem | None]:
        if await self._repo.get_mini(body.id) is not None:
            return ("exists", None)
        so = await self._repo.max_mini_sort_order() + 1
        row = NewsMini(
            id=body.id,
            title=body.title,
            image_url=body.image_url,
            details_url=body.details_url,
            sort_order=so,
            author_user_id=user.id,
        )
        await self._repo.add_mini(row)
        return ("ok", _mini_to_schema(row))

    async def update_news_mini(
        self,
        user: User,
        news_id: str,
        body: NewsMiniUpdateBody,
    ) -> tuple[Literal["ok", "not_found", "forbidden"], NewsMiniItem | None]:
        row = await self._repo.get_mini(news_id)
        if row is None:
            return ("not_found", None)
        if not can_edit_content(user, row.author_user_id):
            return ("forbidden", None)
        if body.title is not None:
            row.title = body.title
        if body.image_url is not None:
            row.image_url = body.image_url
        if body.details_url is not None:
            row.details_url = body.details_url
        return ("ok", _mini_to_schema(row))

    async def delete_news_mini(
        self,
        user: User,
        news_id: str,
    ) -> Literal["ok", "not_found", "forbidden"]:
        row = await self._repo.get_mini(news_id)
        if row is None:
            return "not_found"
        if not can_edit_content(user, row.author_user_id):
            return "forbidden"
        await self._repo.delete_mini(news_id)
        return "ok"

    async def create_news_featured(
        self,
        user: User,
        body: NewsFeaturedCreateBody,
    ) -> tuple[Literal["ok", "exists", "forbidden"], FeaturedNewsItem | None]:
        if not is_moderator_or_admin(user):
            return ("forbidden", None)
        if await self._repo.get_featured(body.id) is not None:
            return ("exists", None)
        so = await self._repo.max_featured_sort_order() + 1
        row = NewsFeatured(
            id=body.id,
            title=body.title,
            subtitle=body.subtitle,
            description=body.description,
            image_url=body.image_url,
            cta_label=body.cta_label,
            details_url=body.details_url,
            sort_order=so,
            author_user_id=user.id,
        )
        await self._repo.add_featured(row)
        return ("ok", _featured_to_schema(row))

    async def update_news_featured(
        self,
        user: User,
        news_id: str,
        body: NewsFeaturedUpdateBody,
    ) -> tuple[Literal["ok", "not_found", "forbidden"], FeaturedNewsItem | None]:
        if not is_moderator_or_admin(user):
            return ("forbidden", None)
        row = await self._repo.get_featured(news_id)
        if row is None:
            return ("not_found", None)
        if body.title is not None:
            row.title = body.title
        if body.subtitle is not None:
            row.subtitle = body.subtitle
        if body.description is not None:
            row.description = body.description
        if body.image_url is not None:
            row.image_url = body.image_url
        if body.cta_label is not None:
            row.cta_label = body.cta_label
        if body.details_url is not None:
            row.details_url = body.details_url
        return ("ok", _featured_to_schema(row))

    async def delete_news_featured(
        self,
        user: User,
        news_id: str,
    ) -> Literal["ok", "not_found", "forbidden"]:
        if not is_moderator_or_admin(user):
            return "forbidden"
        row = await self._repo.get_featured(news_id)
        if row is None:
            return "not_found"
        await self._repo.delete_featured(news_id)
        return "ok"

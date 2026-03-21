from __future__ import annotations

from app.modules.news.repository import NewsRepository
from app.modules.news.models import NewsFeatured, NewsMini
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

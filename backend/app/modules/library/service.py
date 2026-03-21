from __future__ import annotations

from app.modules.library.models import LibraryArticle, LibraryShowcaseItem, LibraryTag
from app.modules.library.repository import LibraryRepository
from schemas import ArticleTag, LibraryArticle as LibraryArticleSchema, LibraryBundle, LibraryHero, LibraryShowcaseItem as LibraryShowcaseSchema, InterestOption


def _hero_from_json(data: object) -> LibraryHero:
    return LibraryHero.model_validate(data)


def _showcase_to_schema(row: LibraryShowcaseItem) -> LibraryShowcaseSchema:
    return LibraryShowcaseSchema(
        id=row.id,
        brandLabel=row.brand_label,
        eyebrow=row.eyebrow,
        title=row.title,
        imageUrl=row.image_url,
        hero=_hero_from_json(row.hero_json),
    )


def _tags_to_schema(tags: list[LibraryTag]) -> list[ArticleTag]:
    return [ArticleTag(id=t.id, label=t.label, tone=t.tone) for t in tags]


def _article_to_schema(row: LibraryArticle, tags: list[LibraryTag]) -> LibraryArticleSchema:
    return LibraryArticleSchema(
        id=row.id,
        tags=_tags_to_schema(tags),
        title=row.title,
        description=row.description,
        authorName=row.author_name,
        authorAvatarUrl=row.author_avatar_url,
    )


class LibraryService:
    def __init__(self, repo: LibraryRepository) -> None:
        self._repo = repo

    async def get_bundle(self) -> LibraryBundle:
        showcase = await self._repo.list_showcase_ordered()
        interests = await self._repo.list_interests_ordered()
        articles_rows = await self._repo.list_articles_ordered()
        articles: list[LibraryArticleSchema] = []
        for a in articles_rows:
            tags = await self._repo.list_tags_for_article(a.id)
            articles.append(_article_to_schema(a, tags))
        return LibraryBundle(
            showcaseItems=[_showcase_to_schema(s) for s in showcase],
            interestOptions=[
                InterestOption(id=o.id, label=o.label, selected=o.selected) for o in interests
            ],
            articles=articles,
        )

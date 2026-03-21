from __future__ import annotations

from typing import Literal

from app.core.permissions import can_edit_content
from app.modules.auth.models import User
from app.modules.library.models import (
    LibraryArticle,
    LibraryInterestOption,
    LibraryShowcaseItem,
    LibraryTag,
)
from app.modules.library.repository import LibraryRepository
from app.modules.library.schemas import (
    InterestOptionCreateBody,
    InterestOptionUpdateBody,
    LibraryArticleCreateBody,
    LibraryArticleUpdateBody,
    LibraryTagCreateBody,
    LibraryTagUpdateBody,
    ShowcaseCreateBody,
    ShowcaseUpdateBody,
)
from schemas import (
    ArticleTag,
    InterestOption,
    LibraryBundle,
    LibraryHero,
)
from schemas import (
    LibraryArticle as LibraryArticleSchema,
)
from schemas import (
    LibraryShowcaseItem as LibraryShowcaseSchema,
)


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


def _article_to_schema(
    row: LibraryArticle,
    tags: list[LibraryTag],
    interest_ids: list[str],
) -> LibraryArticleSchema:
    return LibraryArticleSchema(
        id=row.id,
        tags=_tags_to_schema(tags),
        title=row.title,
        description=row.description,
        authorName=row.author_name,
        authorAvatarUrl=row.author_avatar_url,
        interestIds=interest_ids,
    )


class LibraryService:
    def __init__(self, repo: LibraryRepository) -> None:
        self._repo = repo

    async def get_bundle(self) -> LibraryBundle:
        showcase = await self._repo.list_showcase_ordered()
        interests = await self._repo.list_interests_ordered()
        articles_rows = await self._repo.list_articles_ordered()
        interest_by_article = await self._repo.list_interest_ids_for_articles([a.id for a in articles_rows])
        articles: list[LibraryArticleSchema] = []
        for a in articles_rows:
            tags = await self._repo.list_tags_for_article(a.id)
            iids = interest_by_article.get(a.id, [])
            articles.append(_article_to_schema(a, tags, iids))
        return LibraryBundle(
            showcaseItems=[_showcase_to_schema(s) for s in showcase],
            interestOptions=[
                InterestOption(id=o.id, label=o.label, selected=o.selected) for o in interests
            ],
            articles=articles,
        )

    async def create_article(
        self,
        user: User,
        body: LibraryArticleCreateBody,
    ) -> tuple[Literal["ok", "exists", "bad_tags"], LibraryArticleSchema | None]:
        if await self._repo.get_article(body.id) is not None:
            return ("exists", None)
        if not await self._repo.all_tag_ids_exist(body.tag_ids):
            return ("bad_tags", None)
        row = LibraryArticle(
            id=body.id,
            title=body.title,
            description=body.description,
            author_name=body.author_name,
            author_avatar_url=body.author_avatar_url,
            owner_user_id=user.id,
        )
        await self._repo.add_article(row)
        await self._repo.replace_article_tags(body.id, list(body.tag_ids))
        await self._repo.flush()
        tags = await self._repo.list_tags_for_article(body.id)
        iids = (await self._repo.list_interest_ids_for_articles([body.id])).get(body.id, [])
        await self._repo.commit()
        return ("ok", _article_to_schema(row, tags, iids))

    async def update_article(
        self,
        user: User,
        article_id: str,
        body: LibraryArticleUpdateBody,
    ) -> tuple[Literal["ok", "not_found", "forbidden", "bad_tags"], LibraryArticleSchema | None]:
        row = await self._repo.get_article(article_id)
        if row is None:
            return ("not_found", None)
        if not can_edit_content(user, row.owner_user_id):
            return ("forbidden", None)
        if body.tag_ids is not None and not await self._repo.all_tag_ids_exist(body.tag_ids):
            return ("bad_tags", None)
        if body.title is not None:
            row.title = body.title
        if body.description is not None:
            row.description = body.description
        if body.author_name is not None:
            row.author_name = body.author_name
        if body.author_avatar_url is not None:
            row.author_avatar_url = body.author_avatar_url
        if body.tag_ids is not None:
            await self._repo.replace_article_tags(article_id, list(body.tag_ids))
        await self._repo.flush()
        tags = await self._repo.list_tags_for_article(article_id)
        iids = (await self._repo.list_interest_ids_for_articles([article_id])).get(article_id, [])
        await self._repo.commit()
        return ("ok", _article_to_schema(row, tags, iids))

    async def delete_article(
        self,
        user: User,
        article_id: str,
    ) -> Literal["ok", "not_found", "forbidden"]:
        row = await self._repo.get_article(article_id)
        if row is None:
            return "not_found"
        if not can_edit_content(user, row.owner_user_id):
            return "forbidden"
        await self._repo.delete_article(article_id)
        await self._repo.commit()
        return "ok"

    async def admin_create_showcase(
        self,
        body: ShowcaseCreateBody,
    ) -> tuple[Literal["ok", "exists"], LibraryShowcaseSchema | None]:
        if await self._repo.get_showcase(body.id) is not None:
            return ("exists", None)
        so = await self._repo.max_showcase_sort_order() + 1
        row = LibraryShowcaseItem(
            id=body.id,
            brand_label=body.brand_label,
            eyebrow=body.eyebrow,
            title=body.title,
            image_url=body.image_url,
            hero_json=body.hero.model_dump(),
            sort_order=so,
        )
        await self._repo.add_showcase(row)
        return ("ok", _showcase_to_schema(row))

    async def admin_update_showcase(
        self,
        item_id: str,
        body: ShowcaseUpdateBody,
    ) -> tuple[Literal["ok", "not_found"], LibraryShowcaseSchema | None]:
        row = await self._repo.get_showcase(item_id)
        if row is None:
            return ("not_found", None)
        if body.brand_label is not None:
            row.brand_label = body.brand_label
        if body.eyebrow is not None:
            row.eyebrow = body.eyebrow
        if body.title is not None:
            row.title = body.title
        if body.image_url is not None:
            row.image_url = body.image_url
        if body.hero is not None:
            row.hero_json = body.hero.model_dump()
        if body.sort_order is not None:
            row.sort_order = body.sort_order
        return ("ok", _showcase_to_schema(row))

    async def admin_delete_showcase(self, item_id: str) -> Literal["ok", "not_found"]:
        if await self._repo.delete_showcase(item_id):
            return "ok"
        return "not_found"

    async def admin_create_interest(
        self,
        body: InterestOptionCreateBody,
    ) -> tuple[Literal["ok", "exists"], InterestOption | None]:
        if await self._repo.get_interest(body.id) is not None:
            return ("exists", None)
        so = await self._repo.max_interest_sort_order() + 1
        row = LibraryInterestOption(
            id=body.id,
            label=body.label,
            selected=body.selected,
            sort_order=so,
        )
        await self._repo.add_interest(row)
        return ("ok", InterestOption(id=row.id, label=row.label, selected=row.selected))

    async def admin_update_interest(
        self,
        interest_id: str,
        body: InterestOptionUpdateBody,
    ) -> tuple[Literal["ok", "not_found"], InterestOption | None]:
        row = await self._repo.get_interest(interest_id)
        if row is None:
            return ("not_found", None)
        if body.label is not None:
            row.label = body.label
        if body.selected is not None:
            row.selected = body.selected
        if body.sort_order is not None:
            row.sort_order = body.sort_order
        return ("ok", InterestOption(id=row.id, label=row.label, selected=row.selected))

    async def admin_delete_interest(self, interest_id: str) -> Literal["ok", "not_found"]:
        if await self._repo.delete_interest(interest_id):
            return "ok"
        return "not_found"

    async def admin_create_tag(
        self,
        body: LibraryTagCreateBody,
    ) -> tuple[Literal["ok", "exists"], ArticleTag | None]:
        if await self._repo.get_tag(body.id) is not None:
            return ("exists", None)
        row = LibraryTag(
            id=body.id,
            label=body.label,
            tone=body.tone,
            sort_order=body.sort_order,
        )
        await self._repo.add_tag(row)
        return ("ok", ArticleTag(id=row.id, label=row.label, tone=row.tone))

    async def admin_update_tag(
        self,
        tag_id: str,
        body: LibraryTagUpdateBody,
    ) -> tuple[Literal["ok", "not_found"], ArticleTag | None]:
        row = await self._repo.get_tag(tag_id)
        if row is None:
            return ("not_found", None)
        if body.label is not None:
            row.label = body.label
        if body.tone is not None:
            row.tone = body.tone
        if body.sort_order is not None:
            row.sort_order = body.sort_order
        return ("ok", ArticleTag(id=row.id, label=row.label, tone=row.tone))

    async def admin_delete_tag(self, tag_id: str) -> Literal["ok", "not_found", "in_use"]:
        if await self._repo.get_tag(tag_id) is None:
            return "not_found"
        if await self._repo.article_references_tag(tag_id):
            return "in_use"
        if await self._repo.delete_tag(tag_id):
            return "ok"
        return "not_found"

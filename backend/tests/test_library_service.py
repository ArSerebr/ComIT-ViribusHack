"""LibraryService article CRUD (mocked repo)."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.modules.library.models import LibraryArticle, LibraryInterestOption, LibraryShowcaseItem, LibraryTag
from app.modules.library.schemas import LibraryArticleCreateBody, LibraryArticleUpdateBody
from app.modules.library.service import LibraryService


def _user(role: str, uid: uuid.UUID | None = None) -> MagicMock:
    u = MagicMock()
    u.id = uid or uuid.uuid4()
    u.role = role
    return u


def _tag(tid: str) -> LibraryTag:
    t = MagicMock(spec=LibraryTag)
    t.id = tid
    t.label = "L"
    t.tone = "n"
    return t


@pytest.mark.asyncio
async def test_create_article_sets_owner_and_tags():
    repo = AsyncMock()
    repo.get_article = AsyncMock(return_value=None)
    repo.all_tag_ids_exist = AsyncMock(return_value=True)
    repo.add_article = AsyncMock()
    repo.replace_article_tags = AsyncMock()
    repo.list_tags_for_article = AsyncMock(return_value=[_tag("t1")])
    repo.list_interest_ids_for_articles = AsyncMock(return_value={"art-1": ["ml-engineering"]})

    uid = uuid.uuid4()
    user = _user("user", uid)
    body = LibraryArticleCreateBody(
        id="art-1",
        title="T",
        description="D",
        author_name="A",
        author_avatar_url="https://x/a.png",
        tag_ids=["t1"],
    )
    svc = LibraryService(repo)
    status, art = await svc.create_article(user, body)

    assert status == "ok"
    assert art is not None
    assert art.id == "art-1"
    assert art.interestIds == ["ml-engineering"]
    call = repo.add_article.call_args[0][0]
    assert isinstance(call, LibraryArticle)
    assert call.owner_user_id == uid


@pytest.mark.asyncio
async def test_update_article_forbidden_for_stranger():
    owner = uuid.uuid4()
    row = LibraryArticle(
        id="a1",
        title="t",
        description="d",
        author_name="n",
        author_avatar_url="u",
        owner_user_id=owner,
    )
    repo = AsyncMock()
    repo.get_article = AsyncMock(return_value=row)
    svc = LibraryService(repo)
    status, _ = await svc.update_article(
        _user("user", uuid.uuid4()),
        "a1",
        LibraryArticleUpdateBody(title="X"),
    )
    assert status == "forbidden"


@pytest.mark.asyncio
async def test_update_article_ok_for_moderator_on_foreign():
    owner = uuid.uuid4()
    row = LibraryArticle(
        id="a1",
        title="t",
        description="d",
        author_name="n",
        author_avatar_url="u",
        owner_user_id=owner,
    )
    repo = AsyncMock()
    repo.get_article = AsyncMock(return_value=row)
    repo.list_tags_for_article = AsyncMock(return_value=[])
    repo.list_interest_ids_for_articles = AsyncMock(return_value={"a1": []})
    svc = LibraryService(repo)
    status, art = await svc.update_article(
        _user("moderator", uuid.uuid4()),
        "a1",
        LibraryArticleUpdateBody(title="New"),
    )
    assert status == "ok"
    assert art is not None
    assert row.title == "New"


@pytest.mark.asyncio
async def test_get_bundle_includes_interest_ids_per_article():
    showcase = MagicMock(spec=LibraryShowcaseItem)
    showcase.id = "s1"
    showcase.brand_label = "b"
    showcase.eyebrow = "e"
    showcase.title = "t"
    showcase.image_url = "https://i"
    showcase.hero_json = {
        "id": "h",
        "title": "ht",
        "updatedLabel": "u",
        "providerLabel": "p",
        "description": "d",
    }
    showcase.sort_order = 0

    opt = MagicMock(spec=LibraryInterestOption)
    opt.id = "ml-engineering"
    opt.label = "ML"
    opt.selected = True
    opt.sort_order = 0

    article_row = LibraryArticle(
        id="art-1",
        title="T",
        description="D",
        author_name="A",
        author_avatar_url="https://x/a.png",
        owner_user_id=None,
    )
    tag = _tag("ml")

    repo = AsyncMock()
    repo.list_showcase_ordered = AsyncMock(return_value=[showcase])
    repo.list_interests_ordered = AsyncMock(return_value=[opt])
    repo.list_articles_ordered = AsyncMock(return_value=[article_row])
    repo.list_tags_for_article = AsyncMock(return_value=[tag])
    repo.list_interest_ids_for_articles = AsyncMock(return_value={"art-1": ["backend", "ml-engineering"]})

    bundle = await LibraryService(repo).get_bundle()

    assert len(bundle.articles) == 1
    assert bundle.articles[0].interestIds == ["backend", "ml-engineering"]
    repo.list_interest_ids_for_articles.assert_awaited_once_with(["art-1"])

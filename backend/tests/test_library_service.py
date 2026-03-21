"""LibraryService article CRUD (mocked repo)."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.modules.library.models import LibraryArticle, LibraryTag
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
    svc = LibraryService(repo)
    status, art = await svc.update_article(
        _user("moderator", uuid.uuid4()),
        "a1",
        LibraryArticleUpdateBody(title="New"),
    )
    assert status == "ok"
    assert art is not None
    assert row.title == "New"

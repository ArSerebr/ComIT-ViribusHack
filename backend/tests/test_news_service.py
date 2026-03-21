"""NewsService write paths (mocked repo)."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.modules.news.models import NewsFeatured, NewsMini
from app.modules.news.schemas import NewsFeaturedCreateBody, NewsMiniCreateBody
from app.modules.news.service import NewsService


def _user(role: str, uid: uuid.UUID | None = None) -> MagicMock:
    u = MagicMock()
    u.id = uid or uuid.uuid4()
    u.role = role
    return u


@pytest.mark.asyncio
async def test_create_mini_sets_author():
    repo = AsyncMock()
    repo.get_mini = AsyncMock(return_value=None)
    repo.max_mini_sort_order = AsyncMock(return_value=0)
    repo.add_mini = AsyncMock()
    uid = uuid.uuid4()
    user = _user("user", uid)
    body = NewsMiniCreateBody(
        id="n1",
        title="T",
        image_url="https://i/img.jpg",
        details_url="/news/n1",
    )
    svc = NewsService(repo)
    status, item = await svc.create_news_mini(user, body)
    assert status == "ok"
    assert item is not None
    row = repo.add_mini.call_args[0][0]
    assert isinstance(row, NewsMini)
    assert row.author_user_id == uid


@pytest.mark.asyncio
async def test_create_featured_forbidden_for_plain_user():
    repo = AsyncMock()
    svc = NewsService(repo)
    body = NewsFeaturedCreateBody(
        id="f1",
        title="T",
        subtitle="S",
        description="D",
        image_url="https://i/x.jpg",
        cta_label="Go",
        details_url="/f",
    )
    status, item = await svc.create_news_featured(_user("user"), body)
    assert status == "forbidden"
    assert item is None


@pytest.mark.asyncio
async def test_create_featured_ok_for_moderator():
    repo = AsyncMock()
    repo.get_featured = AsyncMock(return_value=None)
    repo.max_featured_sort_order = AsyncMock(return_value=0)
    repo.add_featured = AsyncMock()
    body = NewsFeaturedCreateBody(
        id="f1",
        title="T",
        subtitle="S",
        description="D",
        image_url="https://i/x.jpg",
        cta_label="Go",
        details_url="/f",
    )
    svc = NewsService(repo)
    status, item = await svc.create_news_featured(_user("moderator"), body)
    assert status == "ok"
    assert item is not None
    row = repo.add_featured.call_args[0][0]
    assert isinstance(row, NewsFeatured)

"""Groupchat router: token and users endpoints."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.modules.auth.deps import current_active_user
from app.modules.auth.models import User
from app.modules.groupchat.deps import get_groupchat_service
from app.modules.groupchat.service import GroupChatService


@pytest.mark.asyncio
async def test_get_token_requires_auth():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        resp = await client.get("/api/groupchat/token")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_post_users_requires_auth():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        resp = await client.post(
            "/api/groupchat/users",
            json={"user_ids": [str(uuid.uuid4())]},
        )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_token_200_with_auth():
    uid = uuid.uuid4()
    fake_user = MagicMock(spec=User)
    fake_user.id = uid

    async def fake_current_user():
        return fake_user

    mock_svc = MagicMock(spec=GroupChatService)
    mock_svc.fetch_token = AsyncMock(return_value="qmsg-jwt-xyz")

    def fake_get_svc():
        return mock_svc

    app.dependency_overrides[current_active_user] = fake_current_user
    app.dependency_overrides[get_groupchat_service] = fake_get_svc
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get("/api/groupchat/token")
        assert resp.status_code == 200
        data = resp.json()
        assert data["access_token"] == "qmsg-jwt-xyz"
        mock_svc.fetch_token.assert_awaited_once_with(uid)
    finally:
        app.dependency_overrides.pop(current_active_user, None)
        app.dependency_overrides.pop(get_groupchat_service, None)


@pytest.mark.asyncio
async def test_groupchat_routes_in_openapi():
    openapi = app.openapi()
    paths = openapi.get("paths", {})
    assert "/api/groupchat/token" in paths
    assert "get" in paths["/api/groupchat/token"]
    assert "/api/groupchat/users" in paths
    assert "post" in paths["/api/groupchat/users"]

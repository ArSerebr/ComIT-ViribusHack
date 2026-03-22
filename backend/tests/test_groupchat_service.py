"""GroupChatService: token fetch, user display info."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.modules.groupchat.client import QmsgCoreClient
from app.modules.groupchat.service import GroupChatService
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_fetch_token_delegates_to_client():
    client = MagicMock(spec=QmsgCoreClient)
    client.fetch_token = AsyncMock(return_value="jwt-token-123")
    svc = GroupChatService(client)
    uid = uuid.uuid4()
    token = await svc.fetch_token(uid)
    assert token == "jwt-token-123"
    client.fetch_token.assert_awaited_once_with(uid)


@pytest.mark.asyncio
async def test_get_user_display_info_merges_auth_and_profile():
    session = MagicMock(spec=AsyncSession)
    uid1 = uuid.uuid4()
    uid2 = uuid.uuid4()
    with (
        patch(
            "app.modules.groupchat.service.auth_api.get_user_emails_by_ids",
            new_callable=AsyncMock,
            return_value={uid1: "a@x.com", uid2: "b@y.com"},
        ),
        patch(
            "app.modules.groupchat.service.profile_api.get_display_names_by_user_ids",
            new_callable=AsyncMock,
            return_value={uid1: "Alice", uid2: None},
        ),
    ):
        client = MagicMock(spec=QmsgCoreClient)
        svc = GroupChatService(client)
        result = await svc.get_user_display_info(session, [uid1, uid2])
    assert len(result) == 2
    by_id = {r["user_id"]: r for r in result}
    assert by_id[uid1]["email"] == "a@x.com"
    assert by_id[uid1]["display_name"] == "Alice"
    assert by_id[uid2]["email"] == "b@y.com"
    assert by_id[uid2]["display_name"] is None


@pytest.mark.asyncio
async def test_get_user_display_info_empty_list():
    session = MagicMock(spec=AsyncSession)
    client = MagicMock(spec=QmsgCoreClient)
    svc = GroupChatService(client)
    result = await svc.get_user_display_info(session, [])
    assert result == []

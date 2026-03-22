"""Groupchat service: token, user lookup, QmsgCore integration."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from app.modules.auth import public_api as auth_api
from app.modules.groupchat.client import QmsgCoreClient
from app.modules.profile import public_api as profile_api
from sqlalchemy.ext.asyncio import AsyncSession


class GroupChatService:
    def __init__(self, client: QmsgCoreClient) -> None:
        self._client = client

    async def fetch_token(self, user_id: uuid.UUID) -> str:
        """Get QmsgCore JWT for the given user."""
        return await self._client.fetch_token(user_id)

    async def get_user_display_info(
        self, session: AsyncSession, user_ids: Sequence[uuid.UUID]
    ) -> list[dict]:
        """Return list of {user_id, display_name, email} for given user IDs."""
        if not user_ids:
            return []
        emails = await auth_api.get_user_emails_by_ids(session, user_ids)
        display_names = await profile_api.get_display_names_by_user_ids(session, list(user_ids))
        result: list[dict] = []
        for uid in user_ids:
            display_name = display_names.get(uid)
            email = emails.get(uid, "")
            result.append(
                {"user_id": uid, "display_name": display_name, "email": email}
            )
        return result

"""Groupchat HTTP schemas."""

from __future__ import annotations

import uuid

from pydantic import BaseModel


class GroupChatTokenResponse(BaseModel):
    access_token: str


class UserDisplayInfo(BaseModel):
    user_id: uuid.UUID
    display_name: str | None
    email: str

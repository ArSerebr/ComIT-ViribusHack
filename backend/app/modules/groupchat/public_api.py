"""Public API for groupchat: create_group, add_member — called from projects module."""

from __future__ import annotations

import uuid

from app.modules.groupchat.client import QmsgCoreClient


async def create_group_for_project(
    project_name: str, owner_user_id: uuid.UUID
) -> str:
    """Create a QmsgCore group for a project. Returns group_id (e.g. gr_xxx)."""
    client = QmsgCoreClient()
    token = await client.fetch_token(owner_user_id)
    return await client.create_group(token, project_name)


async def add_member_to_group(group_id: str, owner_user_id: uuid.UUID, user_id: uuid.UUID) -> None:
    """Add a user to a QmsgCore group. Uses owner token for permissions."""
    client = QmsgCoreClient()
    token = await client.fetch_token(owner_user_id)
    await client.add_member(token, group_id, user_id)


async def delete_group(group_id: str, owner_user_id: uuid.UUID) -> None:
    """Delete a QmsgCore group. Uses owner token for permissions."""
    client = QmsgCoreClient()
    token = await client.fetch_token(owner_user_id)
    await client.delete_group(token, group_id)

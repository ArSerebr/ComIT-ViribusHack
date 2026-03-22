"""Groupchat dependencies."""

from __future__ import annotations

from app.core.db.session import get_db
from app.modules.groupchat.client import QmsgCoreClient
from app.modules.groupchat.service import GroupChatService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


def get_qmsg_client() -> QmsgCoreClient:
    return QmsgCoreClient()


def get_groupchat_service(
    client: QmsgCoreClient = Depends(get_qmsg_client),
) -> GroupChatService:
    return GroupChatService(client)

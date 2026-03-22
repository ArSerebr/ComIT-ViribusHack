"""Groupchat HTTP router: token, users batch lookup."""

from __future__ import annotations

import uuid

from app.modules.auth.deps import current_active_user
from app.modules.auth.models import User
from app.modules.groupchat.deps import get_groupchat_service
from app.modules.groupchat.schemas import GroupChatTokenResponse, UserDisplayInfo
from app.modules.groupchat.service import GroupChatService
from app.core.db.session import get_db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/groupchat", tags=["groupchat"])


@router.get("/token", response_model=GroupChatTokenResponse)
async def get_groupchat_token(
    user: User = Depends(current_active_user),
    service: GroupChatService = Depends(get_groupchat_service),
) -> GroupChatTokenResponse:
    """Return QmsgCore JWT for the current user."""
    access_token = await service.fetch_token(user.id)
    return GroupChatTokenResponse(access_token=access_token)


class UsersRequest(BaseModel):
    user_ids: list[uuid.UUID]


@router.post("/users", response_model=list[UserDisplayInfo])
async def get_users_display_info(
    body: UsersRequest,
    user: User = Depends(current_active_user),
    service: GroupChatService = Depends(get_groupchat_service),
    session: AsyncSession = Depends(get_db),
) -> list[UserDisplayInfo]:
    """Batch lookup display_name and email for user IDs (for chat name resolution)."""
    rows = await service.get_user_display_info(session, body.user_ids)
    return [UserDisplayInfo.model_validate(r) for r in rows]

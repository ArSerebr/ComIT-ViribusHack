"""Notifications HTTP adapter: thin router → service only. No DB/repo access."""

from __future__ import annotations

import uuid

from app.modules.auth.deps import current_active_user
from app.modules.auth.models import User
from app.modules.notifications.deps import get_notifications_service
from app.modules.notifications.service import NotificationsService
from fastapi import APIRouter, Depends
from schemas import NotificationItem

router = APIRouter(prefix="/api", tags=["notifications"])


@router.get("/notifications", response_model=list[NotificationItem])
async def get_notifications(
    user: User = Depends(current_active_user),
    service: NotificationsService = Depends(get_notifications_service),
):
    uid = user.id
    if not isinstance(uid, uuid.UUID):
        uid = uuid.UUID(str(uid))
    return await service.list_notifications(uid)

"""Notifications HTTP adapter: thin router → service only. No DB/repo access."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.modules.notifications.deps import get_notifications_service
from app.modules.notifications.service import NotificationsService

router = APIRouter(prefix="/api", tags=["notifications"])


@router.get("/notifications")
async def get_notifications(
    service: NotificationsService = Depends(get_notifications_service),
):
    return await service.list_notifications()

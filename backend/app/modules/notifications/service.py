from __future__ import annotations

from app.modules.notifications.models import NotificationsItem
from app.modules.notifications.repository import NotificationsRepository
from schemas import NotificationItem


def _to_schema(row: NotificationsItem) -> NotificationItem:
    return NotificationItem(
        id=row.id,
        type=row.type,
        title=row.title,
        dateLabel=row.date_label,
        dateCaption=row.date_caption,
        unread=row.unread,
        authorLabel=row.author_label,
        authorName=row.author_name,
        accentText=row.accent_text,
        ctaLabel=row.cta_label,
        path=row.path,
    )


class NotificationsService:
    def __init__(self, repo: NotificationsRepository) -> None:
        self._repo = repo

    async def list_notifications(self) -> list[NotificationItem]:
        rows = await self._repo.list_ordered()
        return [_to_schema(r) for r in rows]

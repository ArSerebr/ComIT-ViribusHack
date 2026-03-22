"""Схемы API хакатонов."""

from uuid import UUID

from pydantic import BaseModel, Field


class HackathonItem(BaseModel):
    """Хакатон в списке."""

    id: UUID
    external_id: str
    source: str
    title: str
    description: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    location: str | None = None
    is_online: bool = False
    prize_pool: str | None = None
    url: str | None = None
    image_url: str | None = None
    organizer: str | None = None
    tags: list[str] | None = None
    status: str = "upcoming"

    model_config = {"from_attributes": True}


class HackathonDetail(HackathonItem):
    """Детали хакатона (включая description_raw для ML)."""

    description_raw: str | None = None
    registration_deadline: str | None = None

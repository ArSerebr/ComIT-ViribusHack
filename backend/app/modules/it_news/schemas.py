from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ItNewsItemOut(BaseModel):
    id: UUID
    source: str
    title: str
    summary: str | None = None
    url: str
    published_at: datetime | None = None

    model_config = {"from_attributes": True}

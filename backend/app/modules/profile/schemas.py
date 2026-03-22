"""Profile module request models for admin CRUD."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UniversityCreateBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    sort_order: int | None = Field(default=None, alias="sortOrder")


class UniversityUpdateBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str | None = None
    sort_order: int | None = Field(default=None, alias="sortOrder")

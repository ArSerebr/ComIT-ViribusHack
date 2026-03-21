"""News write models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class NewsMiniCreateBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    image_url: str = Field(alias="imageUrl")
    details_url: str = Field(alias="detailsUrl")


class NewsMiniUpdateBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str | None = None
    image_url: str | None = Field(default=None, alias="imageUrl")
    details_url: str | None = Field(default=None, alias="detailsUrl")


class NewsFeaturedCreateBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    subtitle: str
    description: str
    image_url: str = Field(alias="imageUrl")
    cta_label: str = Field(alias="ctaLabel")
    details_url: str = Field(alias="detailsUrl")


class NewsFeaturedUpdateBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    image_url: str | None = Field(default=None, alias="imageUrl")
    cta_label: str | None = Field(default=None, alias="ctaLabel")
    details_url: str | None = Field(default=None, alias="detailsUrl")

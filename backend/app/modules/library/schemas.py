"""Library module request/response models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from schemas import LibraryHero


class LibraryArticleCreateBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    description: str
    author_name: str = Field(alias="authorName")
    author_avatar_url: str = Field(alias="authorAvatarUrl")
    tag_ids: list[str] = Field(default_factory=list, alias="tagIds")


class LibraryArticleUpdateBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str | None = None
    description: str | None = None
    author_name: str | None = Field(default=None, alias="authorName")
    author_avatar_url: str | None = Field(default=None, alias="authorAvatarUrl")
    tag_ids: list[str] | None = Field(default=None, alias="tagIds")


class ShowcaseCreateBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    brand_label: str = Field(alias="brandLabel")
    eyebrow: str
    title: str
    image_url: str = Field(alias="imageUrl")
    hero: LibraryHero


class ShowcaseUpdateBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    brand_label: str | None = Field(default=None, alias="brandLabel")
    eyebrow: str | None = None
    title: str | None = None
    image_url: str | None = Field(default=None, alias="imageUrl")
    hero: LibraryHero | None = None
    sort_order: int | None = Field(default=None, alias="sortOrder")


class InterestOptionCreateBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    label: str
    selected: bool = False


class InterestOptionUpdateBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    label: str | None = None
    selected: bool | None = None
    sort_order: int | None = Field(default=None, alias="sortOrder")


class LibraryTagCreateBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    label: str
    tone: str
    sort_order: int | None = Field(default=None, alias="sortOrder")


class LibraryTagUpdateBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    label: str | None = None
    tone: str | None = None
    sort_order: int | None = Field(default=None, alias="sortOrder")

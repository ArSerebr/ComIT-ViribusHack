"""Projects module API schemas (request/response). Router uses these as adapters."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from schemas import (
    IntegrationItem,
    ParticipantRow,
    PersonPreview,
    ProductivityBlock,
    ProgressBlock,
    TodoBlock,
)


class JoinRequest(BaseModel):
    message: str | None = None


class JoinResponse(BaseModel):
    ok: bool = True
    project_id: str


class ProjectCreateBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    column_id: str = Field(alias="columnId")
    code: str
    title: str
    description: str
    team_name: str = Field(alias="teamName")
    updated_label: str = Field(alias="updatedLabel")
    team_avatar_url: str = Field(alias="teamAvatarUrl")
    details_url: str = Field(alias="detailsUrl")
    visibility: Literal["public", "private"] | None = None
    is_hot: bool | None = Field(default=None, alias="isHot")
    owner_name: str = Field(alias="ownerName")
    join_label: str = Field(alias="joinLabel")
    team_caption: str = Field(alias="teamCaption")
    productivity_caption: str = Field(alias="productivityCaption")
    progress_caption: str = Field(alias="progressCaption")
    todo_caption: str = Field(alias="todoCaption")
    integration_caption: str = Field(alias="integrationCaption")
    team_members_preview: list[PersonPreview] = Field(alias="teamMembersPreview")
    productivity: ProductivityBlock
    progress: ProgressBlock
    todo: TodoBlock
    integrations: list[IntegrationItem]
    participants: list[ParticipantRow]


class ProjectUpdateBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    column_id: str | None = Field(default=None, alias="columnId")
    code: str | None = None
    title: str | None = None
    description: str | None = None
    team_name: str | None = Field(default=None, alias="teamName")
    updated_label: str | None = Field(default=None, alias="updatedLabel")
    team_avatar_url: str | None = Field(default=None, alias="teamAvatarUrl")
    details_url: str | None = Field(default=None, alias="detailsUrl")
    visibility: Literal["public", "private"] | None = None
    is_hot: bool | None = Field(default=None, alias="isHot")
    owner_name: str | None = Field(default=None, alias="ownerName")
    join_label: str | None = Field(default=None, alias="joinLabel")
    team_caption: str | None = Field(default=None, alias="teamCaption")
    productivity_caption: str | None = Field(default=None, alias="productivityCaption")
    progress_caption: str | None = Field(default=None, alias="progressCaption")
    todo_caption: str | None = Field(default=None, alias="todoCaption")
    integration_caption: str | None = Field(default=None, alias="integrationCaption")
    team_members_preview: list[PersonPreview] | None = Field(
        default=None, alias="teamMembersPreview"
    )
    productivity: ProductivityBlock | None = None
    progress: ProgressBlock | None = None
    todo: TodoBlock | None = None
    integrations: list[IntegrationItem] | None = None
    participants: list[ParticipantRow] | None = None


class ProjectsColumnCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str


class ProjectsColumnUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str | None = None
    sort_order: int | None = Field(default=None, alias="sortOrder")

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class OkResponse(BaseModel):
    ok: bool = True


class ErrorDetail(BaseModel):
    """Тело ответа HTTPException (например 404)."""

    detail: str


class LikePayload(BaseModel):
    entity: Literal["recommendation", "news"]
    id: str
    ts: int


class InterestsPayload(BaseModel):
    interests: list[str]
    ts: int


class JoinRequest(BaseModel):
    message: str | None = None


class JoinResponse(BaseModel):
    ok: bool = True
    project_id: str


class NewsMiniItem(BaseModel):
    id: str
    title: str
    imageUrl: str
    detailsUrl: str


class FeaturedNewsItem(BaseModel):
    id: str
    title: str
    subtitle: str
    description: str
    imageUrl: str
    ctaLabel: str
    detailsUrl: str


class HubProject(BaseModel):
    id: str
    code: str
    title: str
    description: str
    teamName: str
    updatedLabel: str
    teamAvatarUrl: str
    detailsUrl: str
    visibility: Literal["public", "private"] | None = None
    isHot: bool | None = None


class ProjectColumn(BaseModel):
    id: str
    title: str
    count: int
    projects: list[HubProject]


class PersonPreview(BaseModel):
    id: str
    name: str
    avatarUrl: str
    avatarVariant: str


class ParticipantRow(PersonPreview):
    comitId: str | None = None
    timeInProject: str | None = None
    role: str | None = None
    status: str | None = None
    lastTask: str | None = None


class ProductivityBlock(BaseModel):
    value: str
    delta: str


class ProgressBlock(BaseModel):
    value: str
    percent: int


class TodoBlock(BaseModel):
    task: str
    updatedLabel: str


class IntegrationItem(BaseModel):
    id: str
    brand: str
    description: str
    statusLabel: str
    connectedSince: str


class ProjectDetails(BaseModel):
    id: str
    code: str
    title: str
    ownerName: str
    detailsUrl: str
    joinLabel: str
    teamCaption: str
    productivityCaption: str
    progressCaption: str
    todoCaption: str
    integrationCaption: str
    teamMembersPreview: list[PersonPreview]
    productivity: ProductivityBlock
    progress: ProgressBlock
    todo: TodoBlock
    integrations: list[IntegrationItem]
    participants: list[ParticipantRow]


class LibraryHero(BaseModel):
    id: str
    title: str
    updatedLabel: str
    providerLabel: str
    description: str


class LibraryShowcaseItem(BaseModel):
    id: str
    brandLabel: str
    eyebrow: str
    title: str
    imageUrl: str
    hero: LibraryHero


class InterestOption(BaseModel):
    id: str
    label: str
    selected: bool


class ArticleTag(BaseModel):
    id: str
    label: str
    tone: str


class LibraryArticle(BaseModel):
    id: str
    tags: list[ArticleTag]
    title: str
    description: str
    authorName: str
    authorAvatarUrl: str


class LibraryBundle(BaseModel):
    showcaseItems: list[LibraryShowcaseItem]
    interestOptions: list[InterestOption]
    articles: list[LibraryArticle]


class NotificationItem(BaseModel):
    id: str
    type: str
    title: str
    dateLabel: str
    dateCaption: str
    unread: bool | None = None
    authorLabel: str | None = None
    authorName: str | None = None
    accentText: str | None = None
    ctaLabel: str | None = None
    path: str | None = None


class RecommendationCard(BaseModel):
    id: str
    title: str
    subtitle: str
    image: str
    link: str


class DashboardHomeEvents(BaseModel):
    count: int
    deltaLabel: str


class DashboardHomeProductivity(BaseModel):
    value: str
    deltaLabel: str


class DashboardHomeCourse(BaseModel):
    title: str
    imageUrl: str
    path: str


class DashboardHome(BaseModel):
    events: DashboardHomeEvents
    productivity: DashboardHomeProductivity
    highlightCourse: DashboardHomeCourse


class ProfileInterest(BaseModel):
    id: str
    label: str


class ProfileMe(BaseModel):
    displayName: str | None = None
    bio: str | None = None
    interests: list[ProfileInterest] = Field(default_factory=list)


class ProfileMePatch(BaseModel):
    displayName: str | None = None
    bio: str | None = None
    interestIds: list[str] | None = None


class ProfileInterestsAdd(BaseModel):
    """Добавить интересы к текущему набору (без удаления уже выбранных)."""

    interestIds: list[str] = Field(..., min_length=1)

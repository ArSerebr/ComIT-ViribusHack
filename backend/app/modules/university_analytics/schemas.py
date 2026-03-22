"""University analytics response schemas."""

from __future__ import annotations

from pydantic import BaseModel


class UniversityListItem(BaseModel):
    """University with aggregated metrics for list view."""

    id: str
    name: str
    studentsCount: int
    projectsCount: int
    articlesCount: int
    eventParticipationsCount: int
    joinRequestsCount: int
    interestsCount: int = 0


class UniversityDashboard(BaseModel):
    """Full dashboard for a single university."""

    universityId: str
    universityName: str
    studentsCount: int
    eventParticipationsCount: int
    joinRequestsCount: int
    projectsCount: int
    articlesCount: int
    interestsCount: int = 0

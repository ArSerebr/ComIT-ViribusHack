"""UniversityAnalyticsService: unit tests with mocked public_api."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from app.modules.university_analytics.service import UniversityAnalyticsService


@pytest.mark.asyncio
async def test_list_universities_with_metrics():
    session = AsyncMock()
    with (
        patch(
            "app.modules.university_analytics.service.profile_api"
        ) as profile_api,
    ):
        profile_api.list_universities = AsyncMock(
            return_value=[("msu", "МГУ"), ("hse", "ВШЭ")]
        )
        profile_api.get_profiles_by_university = AsyncMock(
            side_effect=lambda s, uid: (
                [(uuid.uuid4(), "Student 1")] if uid == "msu" else []
            )
        )
        profile_api.count_interests_by_university = AsyncMock(return_value=0)

        with (
            patch(
                "app.modules.university_analytics.service.news_api"
            ) as news_api,
            patch(
                "app.modules.university_analytics.service.analytics_api"
            ) as analytics_api,
            patch(
                "app.modules.university_analytics.service.projects_api"
            ) as projects_api,
            patch(
                "app.modules.university_analytics.service.library_api"
            ) as library_api,
        ):
            news_api.count_participants_by_user_ids = AsyncMock(return_value=2)
            analytics_api.get_join_requests_by_applicant_ids = AsyncMock(
                return_value=[(1, "p1", uuid.uuid4(), datetime.now(timezone.utc))]
            )
            projects_api.get_projects_by_owner_ids = AsyncMock(
                return_value=[("p1", "Proj", uuid.uuid4())]
            )
            library_api.get_articles_by_owner_ids = AsyncMock(
                return_value=[("a1", "Article", "Author", uuid.uuid4())]
            )

            svc = UniversityAnalyticsService(session)
            result = await svc.list_universities_with_metrics()

    assert len(result) == 2
    assert result[0].id == "msu"
    assert result[0].name == "МГУ"
    assert result[0].studentsCount == 1
    assert result[1].id == "hse"
    assert result[1].studentsCount == 0


@pytest.mark.asyncio
async def test_get_dashboard_returns_none_for_unknown_university():
    session = AsyncMock()
    with patch(
        "app.modules.university_analytics.service.profile_api"
    ) as profile_api:
        profile_api.list_universities = AsyncMock(
            return_value=[("msu", "МГУ")]
        )

        svc = UniversityAnalyticsService(session)
        result = await svc.get_dashboard("unknown")

    assert result is None


@pytest.mark.asyncio
async def test_get_dashboard_returns_dashboard_for_university():
    session = AsyncMock()
    uid = uuid.uuid4()
    with (
        patch(
            "app.modules.university_analytics.service.profile_api"
        ) as profile_api,
    ):
        profile_api.list_universities = AsyncMock(
            return_value=[("msu", "МГУ")]
        )
        profile_api.get_profiles_by_university = AsyncMock(
            return_value=[(uid, "Student A")]
        )
        profile_api.count_interests_by_university = AsyncMock(return_value=3)

        with (
            patch(
                "app.modules.university_analytics.service.news_api"
            ) as news_api,
            patch(
                "app.modules.university_analytics.service.analytics_api"
            ) as analytics_api,
            patch(
                "app.modules.university_analytics.service.projects_api"
            ) as projects_api,
            patch(
                "app.modules.university_analytics.service.library_api"
            ) as library_api,
        ):
            news_api.count_participants_by_user_ids = AsyncMock(
                return_value=5
            )
            analytics_api.get_join_requests_by_applicant_ids = AsyncMock(
                return_value=[(1, "p1", uid, datetime.now(timezone.utc))]
            )
            projects_api.get_projects_by_owner_ids = AsyncMock(
                return_value=[("p1", "Project 1", uid)]
            )
            library_api.get_articles_by_owner_ids = AsyncMock(
                return_value=[("a1", "Article 1", "Author", uid)]
            )

            svc = UniversityAnalyticsService(session)
            result = await svc.get_dashboard("msu")

    assert result is not None
    assert result.universityId == "msu"
    assert result.universityName == "МГУ"
    assert result.studentsCount == 1
    assert result.eventParticipationsCount == 5
    assert result.joinRequestsCount == 1
    assert result.projectsCount == 1
    assert result.articlesCount == 1
    assert result.interestsCount == 3


@pytest.mark.asyncio
async def test_export_students_csv_returns_none_for_unknown_university():
    session = AsyncMock()
    with patch(
        "app.modules.university_analytics.service.profile_api"
    ) as profile_api:
        profile_api.list_universities = AsyncMock(
            return_value=[("msu", "МГУ")]
        )

        svc = UniversityAnalyticsService(session)
        result = await svc.export_students_csv("unknown")

    assert result is None


@pytest.mark.asyncio
async def test_export_students_csv_generates_csv():
    session = AsyncMock()
    uid = uuid.uuid4()
    with patch(
        "app.modules.university_analytics.service.profile_api"
    ) as profile_api:
        profile_api.list_universities = AsyncMock(
            return_value=[("msu", "МГУ")]
        )
        profile_api.get_profiles_by_university = AsyncMock(
            return_value=[(uid, "Student One")]
        )

        svc = UniversityAnalyticsService(session)
        result = await svc.export_students_csv("msu")

    assert result is not None
    assert "\ufeff" in result  # BOM
    assert "user_id" in result
    assert "display_name" in result
    assert "university_name" in result
    assert "Student One" in result
    assert "МГУ" in result
    assert ";" in result  # delimiter

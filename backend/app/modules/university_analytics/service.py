"""University analytics service — orchestrates cross-module public_api calls."""

from __future__ import annotations

import asyncio
import csv
import io
import uuid

from app.modules.analytics import public_api as analytics_api
from app.modules.library import public_api as library_api
from app.modules.news import public_api as news_api
from app.modules.profile import public_api as profile_api
from app.modules.projects import public_api as projects_api
from app.modules.university_analytics.schemas import UniversityDashboard, UniversityListItem
from sqlalchemy.ext.asyncio import AsyncSession


def _display_name(name: str | None) -> str:
    return name or "—"


class UniversityAnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_universities_with_metrics(self) -> list[UniversityListItem]:
        """List all universities with aggregated metrics."""
        universities = await profile_api.list_universities(self._session)
        result: list[UniversityListItem] = []
        for uid, uname in universities:
            dash = await self.get_dashboard(uid)
            if dash is not None:
                result.append(
                    UniversityListItem(
                        id=uid,
                        name=uname,
                        studentsCount=dash.studentsCount,
                        projectsCount=dash.projectsCount,
                        articlesCount=dash.articlesCount,
                        eventParticipationsCount=dash.eventParticipationsCount,
                        joinRequestsCount=dash.joinRequestsCount,
                        interestsCount=dash.interestsCount,
                    )
                )
        return result

    async def get_dashboard(self, university_id: str) -> UniversityDashboard | None:
        """Get dashboard for a single university."""
        universities = await profile_api.list_universities(self._session)
        uname_map = {uid: uname for uid, uname in universities}
        if university_id not in uname_map:
            return None

        profiles = await profile_api.get_profiles_by_university(
            self._session, university_id
        )
        user_ids = [p[0] for p in profiles]

        if not user_ids:
            interests_count = await profile_api.count_interests_by_university(
                self._session, university_id
            )
            return UniversityDashboard(
                universityId=university_id,
                universityName=uname_map[university_id],
                studentsCount=0,
                eventParticipationsCount=0,
                joinRequestsCount=0,
                projectsCount=0,
                articlesCount=0,
                interestsCount=interests_count,
            )

        (
            event_count,
            join_count,
            projects_data,
            articles_data,
            interests_count,
        ) = await self._fetch_metrics_for_dashboard(university_id, user_ids)

        return UniversityDashboard(
            universityId=university_id,
            universityName=uname_map[university_id],
            studentsCount=len(profiles),
            eventParticipationsCount=event_count,
            joinRequestsCount=join_count,
            projectsCount=len(projects_data),
            articlesCount=len(articles_data),
            interestsCount=interests_count,
        )

    async def _fetch_metrics_for_dashboard(
        self, university_id: str, user_ids: list[uuid.UUID]
    ) -> tuple[int, int, list, list, int]:
        """Fetch all metrics; interests_count requires university_id."""
        (
            event_count,
            join_requests_data,
            projects_data,
            articles_data,
            interests_count,
        ) = await asyncio.gather(
            news_api.count_participants_by_user_ids(self._session, user_ids),
            analytics_api.get_join_requests_by_applicant_ids(
                self._session, user_ids
            ),
            projects_api.get_projects_by_owner_ids(self._session, user_ids),
            library_api.get_articles_by_owner_ids(self._session, user_ids),
            profile_api.count_interests_by_university(
                self._session, university_id
            ),
        )
        return (
            event_count,
            len(join_requests_data),
            projects_data,
            articles_data,
            interests_count,
        )

    async def export_students_csv(self, university_id: str) -> str | None:
        """Generate CSV content for students. Returns None if university not found."""
        universities = await profile_api.list_universities(self._session)
        uname_map = {uid: uname for uid, uname in universities}
        if university_id not in uname_map:
            return None

        profiles = await profile_api.get_profiles_by_university(
            self._session, university_id
        )
        uname = uname_map[university_id]

        buf = io.StringIO()
        buf.write("\ufeff")  # BOM for Excel UTF-8
        writer = csv.writer(buf, delimiter=";", lineterminator="\n")
        writer.writerow(["user_id", "display_name", "university_name"])
        for user_id, display_name in profiles:
            writer.writerow([str(user_id), _display_name(display_name), uname])
        return buf.getvalue()

    async def export_participation_csv(
        self, university_id: str
    ) -> str | None:
        """Generate CSV content for event participation."""
        universities = await profile_api.list_universities(self._session)
        uname_map = {uid: uname for uid, uname in universities}
        if university_id not in uname_map:
            return None

        profiles = await profile_api.get_profiles_by_university(
            self._session, university_id
        )
        user_ids = [p[0] for p in profiles]
        display_names = {p[0]: _display_name(p[1]) for p in profiles}
        uname = uname_map[university_id]

        participations = await news_api.list_participations_for_export(
            self._session, user_ids
        )

        buf = io.StringIO()
        buf.write("\ufeff")
        writer = csv.writer(buf, delimiter=";", lineterminator="\n")
        writer.writerow(
            ["user_id", "display_name", "event_id", "event_title", "university_name"]
        )
        for user_id, event_id, event_title in participations:
            writer.writerow(
                [
                    str(user_id),
                    display_names.get(user_id, "—"),
                    event_id,
                    event_title,
                    uname,
                ]
            )
        return buf.getvalue()

    async def export_projects_csv(self, university_id: str) -> str | None:
        """Generate CSV content for projects."""
        universities = await profile_api.list_universities(self._session)
        uname_map = {uid: uname for uid, uname in universities}
        if university_id not in uname_map:
            return None

        profiles = await profile_api.get_profiles_by_university(
            self._session, university_id
        )
        user_ids = [p[0] for p in profiles]
        display_names = {p[0]: _display_name(p[1]) for p in profiles}
        uname = uname_map[university_id]

        projects = await projects_api.get_projects_by_owner_ids(
            self._session, user_ids
        )

        buf = io.StringIO()
        buf.write("\ufeff")
        writer = csv.writer(buf, delimiter=";", lineterminator="\n")
        writer.writerow(
            [
                "project_id",
                "title",
                "owner_user_id",
                "owner_display_name",
                "university_name",
            ]
        )
        for project_id, title, owner_user_id in projects:
            owner_name = (
                display_names.get(owner_user_id, "—")
                if owner_user_id
                else "—"
            )
            writer.writerow(
                [
                    project_id,
                    title,
                    str(owner_user_id) if owner_user_id else "",
                    owner_name,
                    uname,
                ]
            )
        return buf.getvalue()

    async def export_articles_csv(self, university_id: str) -> str | None:
        """Generate CSV content for articles."""
        universities = await profile_api.list_universities(self._session)
        uname_map = {uid: uname for uid, uname in universities}
        if university_id not in uname_map:
            return None

        profiles = await profile_api.get_profiles_by_university(
            self._session, university_id
        )
        user_ids = [p[0] for p in profiles]
        uname = uname_map[university_id]

        articles = await library_api.get_articles_by_owner_ids(
            self._session, user_ids
        )

        buf = io.StringIO()
        buf.write("\ufeff")
        writer = csv.writer(buf, delimiter=";", lineterminator="\n")
        writer.writerow(
            [
                "article_id",
                "title",
                "author_name",
                "owner_user_id",
                "university_name",
            ]
        )
        for article_id, title, author_name, owner_user_id in articles:
            writer.writerow(
                [
                    article_id,
                    title,
                    author_name,
                    str(owner_user_id) if owner_user_id else "",
                    uname,
                ]
            )
        return buf.getvalue()

    async def export_join_requests_csv(
        self, university_id: str
    ) -> str | None:
        """Generate CSV content for join requests."""
        universities = await profile_api.list_universities(self._session)
        uname_map = {uid: uname for uid, uname in universities}
        if university_id not in uname_map:
            return None

        profiles = await profile_api.get_profiles_by_university(
            self._session, university_id
        )
        user_ids = [p[0] for p in profiles]
        display_names = {p[0]: _display_name(p[1]) for p in profiles}
        uname = uname_map[university_id]

        requests = await analytics_api.get_join_requests_by_applicant_ids(
            self._session, user_ids
        )

        buf = io.StringIO()
        buf.write("\ufeff")
        writer = csv.writer(buf, delimiter=";", lineterminator="\n")
        writer.writerow(
            [
                "request_id",
                "project_id",
                "applicant_user_id",
                "applicant_display_name",
                "university_name",
                "created_at",
            ]
        )
        for req_id, project_id, applicant_user_id, created_at in requests:
            applicant_name = (
                display_names.get(applicant_user_id, "—")
                if applicant_user_id
                else "—"
            )
            writer.writerow(
                [
                    str(req_id),
                    project_id,
                    str(applicant_user_id) if applicant_user_id else "",
                    applicant_name,
                    uname,
                    created_at.isoformat() if created_at else "",
                ]
            )
        return buf.getvalue()

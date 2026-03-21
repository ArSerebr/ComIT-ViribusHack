from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from project_admin import models


class AdminAuthFlowTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_superuser(
            username="admin@example.com",
            email="admin@example.com",
            password="admin12345",
        )

    def test_admin_login_page_is_available(self) -> None:
        response = self.client.get(reverse("admin:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "username")

    def test_admin_index_requires_authentication(self) -> None:
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])

    def test_admin_index_is_available_for_superuser(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Site administration")


class AdminRegistryTests(TestCase):
    def test_all_expected_models_are_registered(self) -> None:
        expected_models = {
            models.User,
            models.ProjectsColumn,
            models.ProjectsProject,
            models.ProjectsProjectDetail,
            models.LibraryArticle,
            models.NewsFeatured,
            models.NewsMini,
            models.NotificationsItem,
            models.DashboardRecommendation,
            models.AnalyticsLikeEvent,
            models.AnalyticsJoinRequest,
        }
        registered_models = set(admin.site._registry.keys())
        self.assertTrue(expected_models.issubset(registered_models))

    def test_projects_project_admin_configuration(self) -> None:
        model_admin = admin.site._registry[models.ProjectsProject]
        self.assertEqual(
            model_admin.list_display,
            ("id", "code", "team_name", "column", "sort_order", "owner_user_id"),
        )
        self.assertEqual(model_admin.search_fields, ("id", "code", "team_name", "title"))
        self.assertEqual(model_admin.list_filter, ("column", "is_hot", "visibility"))

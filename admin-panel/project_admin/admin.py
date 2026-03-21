from django.contrib import admin

from .models import (
    AnalyticsJoinRequest,
    AnalyticsLikeEvent,
    DashboardRecommendation,
    LibraryArticle,
    NewsFeatured,
    NewsMini,
    NotificationsItem,
    ProjectsColumn,
    ProjectsProject,
    ProjectsProjectDetail,
    User,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "role", "is_active", "is_superuser", "is_verified")
    search_fields = ("email",)
    list_filter = ("role", "is_active", "is_superuser", "is_verified")


@admin.register(ProjectsColumn)
class ProjectsColumnAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "sort_order")
    search_fields = ("id", "title")


@admin.register(ProjectsProject)
class ProjectsProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "team_name", "column", "sort_order", "owner_user_id")
    search_fields = ("id", "code", "team_name", "title")
    list_filter = ("column", "is_hot", "visibility")
    # Новые проекты получают max(sort_order)+1 в колонке — показываем сверху списка.
    ordering = ("-sort_order", "id")


@admin.register(ProjectsProjectDetail)
class ProjectsProjectDetailAdmin(admin.ModelAdmin):
    list_display = ("project", "owner_name", "join_label")
    search_fields = ("project__id", "owner_name")


@admin.register(LibraryArticle)
class LibraryArticleAdmin(admin.ModelAdmin):
    list_display = ("id", "author_name", "owner_user_id")
    search_fields = ("id", "title", "author_name")


@admin.register(NewsFeatured)
class NewsFeaturedAdmin(admin.ModelAdmin):
    list_display = ("id", "cta_label", "sort_order", "author_user_id")
    search_fields = ("id", "title", "subtitle")


@admin.register(NewsMini)
class NewsMiniAdmin(admin.ModelAdmin):
    list_display = ("id", "sort_order", "author_user_id")
    search_fields = ("id", "title")


@admin.register(NotificationsItem)
class NotificationsItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "type", "date_label", "unread", "sort_order")
    search_fields = ("id", "title", "author_name", "user_id")
    list_filter = ("type", "unread")


@admin.register(DashboardRecommendation)
class DashboardRecommendationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "sort_order")
    search_fields = ("id", "title", "subtitle")


@admin.register(AnalyticsLikeEvent)
class AnalyticsLikeEventAdmin(admin.ModelAdmin):
    list_display = ("id", "entity", "entity_id", "ts", "seed_key")
    search_fields = ("entity", "entity_id", "seed_key")


@admin.register(AnalyticsJoinRequest)
class AnalyticsJoinRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "applicant_user_id", "created_at")
    search_fields = ("project__id", "message", "applicant_user_id")

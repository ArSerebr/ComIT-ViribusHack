import uuid

from django.db import models


class User(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    email = models.EmailField(max_length=320)
    role = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = "user"
        managed = False
        verbose_name = "FastAPI user"
        verbose_name_plural = "FastAPI users"

    def __str__(self) -> str:
        return self.email


class ProjectsColumn(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    title = models.CharField(max_length=255)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = "projects_column"
        managed = False

    def __str__(self) -> str:
        return self.title


class ProjectsProject(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    code = models.CharField(max_length=32)
    title = models.TextField()
    description = models.TextField()
    team_name = models.CharField(max_length=255)
    updated_label = models.CharField(max_length=255)
    team_avatar_url = models.CharField(max_length=2048)
    details_url = models.CharField(max_length=2048)
    visibility = models.CharField(max_length=20, null=True, blank=True)
    is_hot = models.BooleanField(null=True, blank=True)
    column = models.ForeignKey(ProjectsColumn, db_column="column_id", on_delete=models.DO_NOTHING)
    sort_order = models.IntegerField(default=0)
    owner_user_id = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "projects_project"
        managed = False

    def __str__(self) -> str:
        return f"{self.code}: {self.team_name}"


class ProjectsProjectDetail(models.Model):
    project = models.OneToOneField(
        ProjectsProject,
        db_column="project_id",
        on_delete=models.DO_NOTHING,
        primary_key=True,
    )
    owner_name = models.CharField(max_length=255)
    join_label = models.CharField(max_length=255)
    team_caption = models.CharField(max_length=255)
    productivity_caption = models.CharField(max_length=255)
    progress_caption = models.CharField(max_length=255)
    todo_caption = models.CharField(max_length=255)
    integration_caption = models.CharField(max_length=255)
    detail_blocks = models.JSONField()

    class Meta:
        db_table = "projects_project_detail"
        managed = False


class LibraryArticle(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    title = models.TextField()
    description = models.TextField()
    author_name = models.CharField(max_length=255)
    author_avatar_url = models.CharField(max_length=2048)
    owner_user_id = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "library_article"
        managed = False

    def __str__(self) -> str:
        return self.title[:80]


class NewsFeatured(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    title = models.TextField()
    subtitle = models.TextField()
    description = models.TextField()
    image_url = models.CharField(max_length=2048)
    cta_label = models.CharField(max_length=255)
    details_url = models.CharField(max_length=2048)
    sort_order = models.IntegerField(default=0)
    author_user_id = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "news_featured"
        managed = False

    def __str__(self) -> str:
        return self.title[:80]


class NewsMini(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    title = models.TextField()
    image_url = models.CharField(max_length=2048)
    details_url = models.CharField(max_length=2048)
    sort_order = models.IntegerField(default=0)
    author_user_id = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "news_mini"
        managed = False

    def __str__(self) -> str:
        return self.title[:80]


class NotificationsItem(models.Model):
    user_id = models.UUIDField(default=uuid.uuid4)
    id = models.CharField(max_length=255, primary_key=True)
    type = models.CharField(max_length=64)
    title = models.TextField()
    date_label = models.CharField(max_length=255)
    date_caption = models.CharField(max_length=255)
    unread = models.BooleanField(null=True, blank=True)
    author_label = models.CharField(max_length=255, null=True, blank=True)
    author_name = models.CharField(max_length=255, null=True, blank=True)
    accent_text = models.CharField(max_length=255, null=True, blank=True)
    cta_label = models.CharField(max_length=255, null=True, blank=True)
    path = models.CharField(max_length=2048, null=True, blank=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = "notifications_item"
        managed = False

    def __str__(self) -> str:
        return self.title[:80]


class DashboardRecommendation(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    title = models.TextField()
    subtitle = models.TextField()
    image = models.CharField(max_length=2048)
    link = models.CharField(max_length=2048)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = "dashboard_recommendation"
        managed = False

    def __str__(self) -> str:
        return self.title[:80]


class AnalyticsLikeEvent(models.Model):
    id = models.BigAutoField(primary_key=True)
    entity = models.CharField(max_length=20)
    entity_id = models.CharField(max_length=255)
    ts = models.BigIntegerField()
    seed_key = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "analytics_like_event"
        managed = False


class AnalyticsJoinRequest(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(ProjectsProject, db_column="project_id", on_delete=models.DO_NOTHING)
    applicant_user_id = models.UUIDField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField()

    class Meta:
        db_table = "analytics_join_request"
        managed = False

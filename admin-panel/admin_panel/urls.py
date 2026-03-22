from django.contrib import admin
from django.http import HttpResponse
from django.urls import path


def health(_request: object) -> HttpResponse:
    """Лёгкий endpoint для Docker/orchestrator без обращения к БД."""
    return HttpResponse("ok", content_type="text/plain")


urlpatterns = [
    path("health/", health),
    path("admin/", admin.site.urls),
]

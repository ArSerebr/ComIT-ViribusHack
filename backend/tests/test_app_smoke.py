"""Smoke: приложение собирается, OpenAPI и документация отдаются без обращения к БД."""

from __future__ import annotations

from app.main import create_app
from fastapi.testclient import TestClient


def test_create_app_exposes_openapi():
    app = create_app()
    with TestClient(app) as client:
        r = client.get("/openapi.json")
    assert r.status_code == 200
    body = r.json()
    assert str(body.get("openapi", "")).startswith("3.")
    assert "paths" in body
    assert "/health" in body["paths"]
    assert "/ready" in body["paths"]
    assert "/api/projects/hub" in body["paths"]
    assert "/api/projects" in body["paths"]
    assert "/api/projects/{project_id}/work-plan/generate" in body["paths"]
    assert "/api/projects/{project_id}/work-plan/assign" in body["paths"]
    assert "/api/profile/me" in body["paths"]
    assert "/api/profile/me/interests" in body["paths"]
    assert "/api/profile/universities" in body["paths"]
    assert "/api/admin/profile/universities" in body["paths"]
    assert "/api/library/articles" in body["paths"]
    assert "/api/admin/projects/columns" in body["paths"]
    assert "/api/news/featured/{news_id}/participate" in body["paths"]
    assert "/api/recommendations/feedback" in body["paths"]
    assert "/api/analytics/universities" in body["paths"]
    assert "/api/analytics/universities/{university_id}/dashboard" in body["paths"]
    assert "/api/analytics/universities/{university_id}/export/students" in body["paths"]
    assert "/api/analytics/universities/{university_id}/export/participation" in body["paths"]
    assert "/api/analytics/universities/{university_id}/export/projects" in body["paths"]
    assert "/api/analytics/universities/{university_id}/export/articles" in body["paths"]
    assert "/api/analytics/universities/{university_id}/export/join-requests" in body["paths"]
    assert "/api/pulse/execute" in body["paths"]
    lib_article = body["components"]["schemas"]["LibraryArticle"]
    assert "interestIds" in lib_article["properties"]
    assert "UniversityListItem" in body["components"]["schemas"]
    assert "UniversityDashboard" in body["components"]["schemas"]


def test_health_live_no_db():
    app = create_app()
    with TestClient(app) as client:
        r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
    assert "X-Request-ID" in r.headers


def test_docs_available():
    app = create_app()
    with TestClient(app) as client:
        r = client.get("/docs")
    assert r.status_code == 200

"""Smoke: приложение собирается, OpenAPI и документация отдаются без обращения к БД."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_create_app_exposes_openapi():
    app = create_app()
    with TestClient(app) as client:
        r = client.get("/openapi.json")
    assert r.status_code == 200
    body = r.json()
    assert str(body.get("openapi", "")).startswith("3.")
    assert "paths" in body
    assert "/api/projects/hub" in body["paths"]


def test_docs_available():
    app = create_app()
    with TestClient(app) as client:
        r = client.get("/docs")
    assert r.status_code == 200

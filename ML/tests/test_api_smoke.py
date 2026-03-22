"""
Smoke test for ML API server.

Run from repo root: python -m pytest ML/tests/test_api_smoke.py -v
Or from ML/: python -m pytest tests/test_api_smoke.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure ML is on path for api_server import
ML_ROOT = Path(__file__).resolve().parent.parent
if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))


@pytest.fixture(scope="module")
def ml_app():
    """Import ML api_server app. Skips if dependencies (e.g. recommender) fail."""
    try:
        from api_server import app
        return app
    except Exception as e:
        pytest.skip(f"ML api_server import failed: {e}")


def test_ml_health(ml_app):
    """ML API /health returns 200."""
    from fastapi.testclient import TestClient
    with TestClient(ml_app) as client:
        r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"
    assert "service" in data


def test_ml_recommend_news_endpoint_exists(ml_app):
    """ML API exposes /recommend/news."""
    openapi = ml_app.openapi()
    paths = openapi.get("paths", {})
    assert "/recommend/news" in paths
    assert "get" in paths["/recommend/news"]


def test_ml_recommend_events_endpoint_exists(ml_app):
    """ML API exposes /recommend/events."""
    openapi = ml_app.openapi()
    paths = openapi.get("paths", {})
    assert "/recommend/events" in paths
    assert "get" in paths["/recommend/events"]


def test_ml_feedback_endpoint_exists(ml_app):
    """ML API exposes POST /feedback."""
    openapi = ml_app.openapi()
    paths = openapi.get("paths", {})
    assert "/feedback" in paths
    assert "post" in paths["/feedback"]

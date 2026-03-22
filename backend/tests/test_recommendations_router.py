"""Recommendations router: feedback endpoint requires auth."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.modules.auth.deps import current_active_user
from app.modules.auth.models import User
from app.modules.recommendations.deps import get_recommendations_service
from app.modules.recommendations.service import RecommendationsService


@pytest.mark.asyncio
async def test_feedback_requires_auth():
    """POST /api/recommendations/feedback returns 401 without auth."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        resp = await client.post(
            "/api/recommendations/feedback",
            json={"entity_id": "card-1", "reaction": "like", "ts": 12345},
        )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_feedback_200_with_auth():
    """POST /api/recommendations/feedback returns 200 with valid auth."""
    uid = uuid.uuid4()
    fake_user = MagicMock(spec=User)
    fake_user.id = uid

    async def fake_current_user():
        return fake_user

    mock_svc = MagicMock(spec=RecommendationsService)
    mock_svc.record_feedback = AsyncMock()

    def fake_get_svc():
        return mock_svc

    app.dependency_overrides[current_active_user] = fake_current_user
    app.dependency_overrides[get_recommendations_service] = fake_get_svc

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.post(
                "/api/recommendations/feedback",
                json={"entity_id": "card-1", "reaction": "like", "ts": 12345},
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("ok") is True
        mock_svc.record_feedback.assert_awaited_once_with(
            user_id=uid,
            entity_id="card-1",
            reaction="like",
            ts=12345,
        )
    finally:
        app.dependency_overrides.pop(current_active_user, None)
        app.dependency_overrides.pop(get_recommendations_service, None)


@pytest.mark.asyncio
async def test_recommendations_routes_in_openapi():
    """Recommendations feedback route is in OpenAPI."""
    openapi = app.openapi()
    paths = openapi.get("paths", {})
    assert "/api/recommendations/feedback" in paths
    assert "post" in paths["/api/recommendations/feedback"]

"""AnalyticsService: запись событий с commit сессии."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from app.modules.analytics.service import AnalyticsService


@pytest.mark.asyncio
async def test_record_like_commits():
    session = AsyncMock()
    session.commit = AsyncMock()
    with patch("app.modules.analytics.service.AnalyticsRepository") as RepoCls:
        repo = RepoCls.return_value
        repo.add_like_event = AsyncMock()
        svc = AnalyticsService(session)
        await svc.record_like(entity="news", entity_id="n1", ts=1000)
        repo.add_like_event.assert_awaited_once_with(entity="news", entity_id="n1", ts=1000)
        session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_record_interests_commits():
    session = AsyncMock()
    session.commit = AsyncMock()
    with patch("app.modules.analytics.service.AnalyticsRepository") as RepoCls:
        repo = RepoCls.return_value
        repo.add_interest_event = AsyncMock()
        svc = AnalyticsService(session)
        await svc.record_interests(interests=["a", "b"], ts=2000)
        repo.add_interest_event.assert_awaited_once_with(interests=["a", "b"], ts=2000)
        session.commit.assert_awaited_once()

"""DashboardService: маппинг репозитория в схемы API."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.dashboard.models import DashboardRecommendation
from app.modules.dashboard.service import DashboardService
from schemas import DashboardHome


@pytest.mark.asyncio
async def test_list_recommendations_maps_rows():
    repo = AsyncMock()
    row = MagicMock(spec=DashboardRecommendation)
    row.id = "r1"
    row.title = "Title"
    row.subtitle = "Sub"
    row.image = "https://i"
    row.link = "https://l"
    repo.list_recommendations_ordered = AsyncMock(return_value=[row])
    svc = DashboardService(repo)

    out = await svc.list_recommendations()

    assert len(out) == 1
    assert out[0].id == "r1"
    assert out[0].title == "Title"


@pytest.mark.asyncio
async def test_get_home_returns_none_when_no_snapshot():
    repo = AsyncMock()
    repo.get_home_snapshot = AsyncMock(return_value=None)
    svc = DashboardService(repo)

    assert await svc.get_home() is None


@pytest.mark.asyncio
async def test_get_home_validates_json_from_snapshot():
    repo = AsyncMock()
    snap = MagicMock()
    snap.home_json = {
        "events": {"count": 2, "deltaLabel": "+1"},
        "productivity": {"value": "80%", "deltaLabel": "week"},
        "highlightCourse": {"title": "Course", "imageUrl": "https://x/i.png", "path": "/learn"},
    }
    repo.get_home_snapshot = AsyncMock(return_value=snap)
    svc = DashboardService(repo)

    home = await svc.get_home()

    assert isinstance(home, DashboardHome)
    assert home.events.count == 2

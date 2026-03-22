"""RecommendationsService: ML integration with mocked ML client."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from schemas import RecommendationCard

from app.modules.recommendations.ml_client import MLRecommendationClient
from app.modules.recommendations.service import RecommendationsService


@pytest.fixture
def mock_ml():
    ml = MagicMock(spec=MLRecommendationClient)
    ml.recommend_news = AsyncMock(return_value=[{"card_id": "c1", "title": "News 1"}])
    ml.recommend_events = AsyncMock(return_value=[{"card_id": "c2", "title": "Event 1"}])
    ml.feedback = AsyncMock(return_value={"ok": True})
    return ml


@pytest.fixture
def session():
    return AsyncMock()


@pytest.mark.asyncio
async def test_list_recommendations_anonymous_returns_static_fallback(session, mock_ml):
    """Anonymous user gets static recommendations from dashboard."""
    with (
        patch(
            "app.modules.recommendations.service.dashboard_public_api"
        ) as dash_api,
    ):
        dash_api.list_recommendation_cards_ordered = AsyncMock(
            return_value=[
                RecommendationCard(
                    id="s1", title="Static", subtitle="", image="", link=""
                )
            ]
        )
        svc = RecommendationsService(session, ml_client=mock_ml)
        out = await svc.list_recommendations(user_id=None)
    assert len(out) == 1
    assert out[0].id == "s1"
    mock_ml.recommend_news.assert_not_awaited()


@pytest.mark.asyncio
async def test_list_recommendations_authenticated_calls_ml_and_resolves(session, mock_ml):
    """Authenticated user gets ML recommendations, cards resolved from DB."""
    user_id = uuid.uuid4()
    resolved = RecommendationCard(
        id="c1", title="Resolved 1", subtitle="", image="img", link="url"
    )
    with (
        patch(
            "app.modules.recommendations.service.news_public_api"
        ) as news_api,
        patch(
            "app.modules.recommendations.service.dashboard_public_api"
        ) as dash_api,
    ):
        news_api.get_featured_cards_by_ids = AsyncMock(return_value=[])
        news_api.get_mini_cards_by_ids = AsyncMock(return_value=[resolved])
        dash_api.get_recommendation_cards_by_ids = AsyncMock(return_value=[])

        svc = RecommendationsService(session, ml_client=mock_ml)
        out = await svc.list_recommendations(user_id=user_id)

    mock_ml.recommend_news.assert_awaited_once_with(str(user_id), limit=10)
    mock_ml.recommend_events.assert_awaited_once_with(str(user_id), limit=10)
    assert len(out) == 1
    assert out[0].id == "c1"
    assert out[0].title == "Resolved 1"


@pytest.mark.asyncio
async def test_list_recommendations_ml_failure_fallback(session, mock_ml):
    """When ML fails, fallback to static recommendations."""
    mock_ml.recommend_news.side_effect = Exception("ML timeout")
    with (
        patch(
            "app.modules.recommendations.service.dashboard_public_api"
        ) as dash_api,
    ):
        dash_api.list_recommendation_cards_ordered = AsyncMock(
            return_value=[
                RecommendationCard(
                    id="fallback", title="Fallback", subtitle="", image="", link=""
                )
            ]
        )
        svc = RecommendationsService(session, ml_client=mock_ml)
        out = await svc.list_recommendations(user_id=uuid.uuid4())
    assert len(out) == 1
    assert out[0].id == "fallback"


@pytest.mark.asyncio
async def test_record_feedback_calls_ml_and_analytics(session, mock_ml):
    """record_feedback proxies to ML and records analytics event."""
    user_id = uuid.uuid4()
    with patch(
        "app.modules.analytics.public_api.record_like_event",
        new_callable=AsyncMock,
    ) as record_like_event:
        svc = RecommendationsService(session, ml_client=mock_ml)
        await svc.record_feedback(
            user_id=user_id,
            entity_id="card-123",
            reaction="like",
            ts=1234567890,
        )

    mock_ml.feedback.assert_awaited_once_with(
        str(user_id), "card-123", "like"
    )
    record_like_event.assert_awaited_once_with(
        session, entity="recommendation", entity_id="card-123", ts=1234567890
    )


@pytest.mark.asyncio
async def test_record_feedback_continues_when_ml_fails(session, mock_ml):
    """record_feedback still records analytics when ML fails."""
    mock_ml.feedback.side_effect = Exception("ML down")
    with patch(
        "app.modules.analytics.public_api.record_like_event",
        new_callable=AsyncMock,
    ) as record_like_event:
        svc = RecommendationsService(session, ml_client=mock_ml)
        await svc.record_feedback(
            user_id=uuid.uuid4(),
            entity_id="card-456",
            reaction="share",
            ts=999,
        )

    record_like_event.assert_awaited_once_with(
        session, entity="recommendation", entity_id="card-456", ts=999
    )

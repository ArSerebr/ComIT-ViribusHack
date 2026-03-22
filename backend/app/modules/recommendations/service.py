"""Recommendations service: ML integration, card mapping, fallback to static."""

from __future__ import annotations

import logging
import uuid

from app.modules.dashboard import public_api as dashboard_public_api
from app.modules.news import public_api as news_public_api
from app.modules.recommendations import public_api as reco_catalog_public_api
from app.modules.recommendations.ml_client import MLRecommendationClient
from schemas import RecommendationCard
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class RecommendationsService:
    def __init__(
        self,
        session: AsyncSession,
        ml_client: MLRecommendationClient | None = None,
    ) -> None:
        self._session = session
        self._ml = ml_client or MLRecommendationClient()

    async def _static_recommendation_cards(self) -> list[RecommendationCard]:
        """
        Dashboard seed cards + recommendation_catalog (CSV/hackathons).
        Same id: catalog row wins; catalog-only ids are appended after dashboard order.
        """
        dash = await dashboard_public_api.list_recommendation_cards_ordered(
            self._session
        )
        catalog = await reco_catalog_public_api.list_recommendation_catalog_ordered(
            self._session
        )
        cat_by_id = {c.id: c for c in catalog}
        out: list[RecommendationCard] = []
        seen: set[str] = set()
        for c in dash:
            merged = cat_by_id.get(c.id, c)
            out.append(merged)
            seen.add(c.id)
        for c in catalog:
            if c.id not in seen:
                out.append(c)
                seen.add(c.id)
        return out

    async def list_recommendations(
        self, user_id: uuid.UUID | None, limit: int = 10
    ) -> list[RecommendationCard]:
        """
        Return personalized recommendations for authenticated user,
        or static fallback for anonymous.
        """
        if user_id is None:
            return await self._static_recommendation_cards()

        try:
            news_recs = await self._ml.recommend_news(str(user_id), limit=limit)
            event_recs = await self._ml.recommend_events(str(user_id), limit=limit)
        except Exception as e:
            logger.warning("ML recommendations failed, using static fallback: %s", e)
            return await self._static_recommendation_cards()

        card_ids = []
        seen: set[str] = set()
        for r in news_recs + event_recs:
            cid = r.get("card_id")
            if cid and cid not in seen:
                seen.add(cid)
                card_ids.append(cid)

        if not card_ids:
            return await self._static_recommendation_cards()

        cards_by_id = await self._resolve_cards(card_ids)
        return [
            cards_by_id[cid]
            for cid in card_ids
            if cid in cards_by_id
        ]

    async def _resolve_cards(
        self, card_ids: list[str]
    ) -> dict[str, RecommendationCard]:
        """Resolve card_ids from news_featured, news_mini, dashboard_recommendation."""
        featured = await news_public_api.get_featured_cards_by_ids(
            self._session, card_ids
        )
        mini = await news_public_api.get_mini_cards_by_ids(self._session, card_ids)
        dashboard = await dashboard_public_api.get_recommendation_cards_by_ids(
            self._session, card_ids
        )
        catalog = await reco_catalog_public_api.get_catalog_cards_by_ids(
            self._session, card_ids
        )
        result: dict[str, RecommendationCard] = {}
        for c in featured + mini + dashboard:
            result[c.id] = c
        for c in catalog:
            result[c.id] = c
        return result

    async def record_feedback(
        self,
        user_id: uuid.UUID,
        entity_id: str,
        reaction: str,
        ts: int,
    ) -> None:
        """
        Proxy feedback to ML and record analytics_like_event (entity=recommendation).
        """
        try:
            await self._ml.feedback(str(user_id), entity_id, reaction)
        except Exception as e:
            logger.warning("ML feedback failed: %s", e)
        await self._record_like_event(entity_id=entity_id, ts=ts)

    async def _record_like_event(self, entity_id: str, ts: int) -> None:
        """Record like in analytics (entity=recommendation)."""
        from app.modules.analytics import public_api as analytics_public_api

        await analytics_public_api.record_like_event(
            self._session,
            entity="recommendation",
            entity_id=entity_id,
            ts=ts,
        )

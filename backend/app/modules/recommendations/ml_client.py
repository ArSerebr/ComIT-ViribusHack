"""HTTP client for ML recommendation service."""

from __future__ import annotations

import httpx

from app.config import get_settings


class MLRecommendationClient:
    """Async client for ML API (recommend/news, recommend/events, feedback)."""

    def __init__(self, base_url: str | None = None) -> None:
        self._base = (
            (base_url or get_settings().ml_service_url).rstrip("/")
        )

    async def recommend_news(self, user_id: str, limit: int = 10) -> list[dict]:
        """GET /recommend/news. Returns list of {card_id, title, ...}."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{self._base}/recommend/news",
                params={"user_id": user_id, "limit": limit},
            )
            resp.raise_for_status()
            return resp.json()

    async def recommend_events(self, user_id: str, limit: int = 10) -> list[dict]:
        """GET /recommend/events. Returns list of {card_id, title, ...}."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{self._base}/recommend/events",
                params={"user_id": user_id, "limit": limit},
            )
            resp.raise_for_status()
            return resp.json()

    async def feedback(self, user_id: str, card_id: str, reaction: str) -> dict:
        """POST /feedback. Returns {ok, user_id, card_id, reaction}."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self._base}/feedback",
                json={"user_id": user_id, "card_id": card_id, "reaction": reaction},
            )
            resp.raise_for_status()
            return resp.json()

"""Recommendations module API schemas (request/response)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class FeedbackPayload(BaseModel):
    """Payload for POST /api/recommendations/feedback."""

    entity_id: str
    reaction: Literal["open", "like", "share", "long_view", "skip_fast", "disengage"]
    ts: int

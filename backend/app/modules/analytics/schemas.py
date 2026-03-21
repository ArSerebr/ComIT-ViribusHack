"""Analytics module API schemas (request/response). Router uses these as adapters."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class OkResponse(BaseModel):
    ok: bool = True


class LikePayload(BaseModel):
    entity: Literal["recommendation", "news"]
    id: str
    ts: int


class InterestsPayload(BaseModel):
    interests: list[str]
    ts: int

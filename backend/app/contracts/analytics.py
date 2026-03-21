from __future__ import annotations

from typing import Protocol


class JoinRequestSink(Protocol):
    """Analytics-owned join-request persistence; called from the projects module."""

    async def record_join_request(self, project_id: str, message: str | None) -> None:
        ...

from __future__ import annotations

from typing import Protocol


class ProjectQueryPort(Protocol):
    """Read-only project lookups for other bounded contexts (no ORM leakage)."""

    async def project_exists(self, project_id: str) -> bool:
        ...

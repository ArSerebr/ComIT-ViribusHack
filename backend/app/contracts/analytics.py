from __future__ import annotations

import uuid
from typing import Protocol


class JoinRequestSink(Protocol):
    """Analytics-owned join-request persistence; called from the projects module."""

    async def record_join_request(
        self,
        project_id: str,
        message: str | None,
        applicant_user_id: uuid.UUID,
    ) -> None: ...

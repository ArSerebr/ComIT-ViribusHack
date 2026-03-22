"""PulseCore proxy service."""

from __future__ import annotations

import uuid

from app.modules.pulse.client import PulseCoreClient


class PulseService:
    """Proxies PulseCore API using user_id as uid."""

    def __init__(self, client: PulseCoreClient) -> None:
        self._client = client

    def _uid(self, user_id: uuid.UUID) -> str:
        return str(user_id)

    async def submit_chat(self, user_id: uuid.UUID, message: str) -> str:
        """Submit chat message. Returns task_id."""
        return await self._client.submit_chat(self._uid(user_id), message)

    async def poll_task(self, task_id: str) -> dict:
        """Poll task status. Returns {status, result?}."""
        return await self._client.poll_task(task_id)

    async def get_status(self, user_id: uuid.UUID) -> dict:
        """Get current status for user."""
        return await self._client.get_status(self._uid(user_id))

    async def get_history(self, user_id: uuid.UUID) -> list[dict]:
        """Get chat history for user."""
        return await self._client.get_history(self._uid(user_id))

    async def execute_task(self, user_id: uuid.UUID) -> dict:
        """Confirm task execution."""
        return await self._client.execute(self._uid(user_id))

    async def cancel_task(self, user_id: uuid.UUID) -> dict:
        """Cancel pending task."""
        return await self._client.cancel(self._uid(user_id))

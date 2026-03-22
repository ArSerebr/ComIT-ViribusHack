"""PulseCore proxy service."""

from __future__ import annotations

import uuid
from typing import Any

from app.modules.agent_demo.service import AgentDemoService, normalize_frontend_actions
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

    async def submit_work_plan(
        self,
        user_id: uuid.UUID,
        *,
        project_title: str,
        project_description: str,
        project_deadline: str,
        project_id_hint: str = "",
    ) -> str:
        """Submit work plan generation. Returns task_id."""
        return await self._client.submit_work_plan(
            self._uid(user_id),
            project_title=project_title,
            project_description=project_description,
            project_deadline=project_deadline,
            project_id_hint=project_id_hint,
        )

    async def poll_task(self, task_id: str) -> dict:
        """Poll task status. Returns {status, result?}."""
        return await self._client.poll_task(task_id)

    async def get_status(self, user_id: uuid.UUID) -> dict:
        """Get current status for user."""
        return await self._client.get_status(self._uid(user_id))

    async def get_history(self, user_id: uuid.UUID) -> list[dict]:
        """Get chat history for user."""
        return await self._client.get_history(self._uid(user_id))

    async def execute_task(self, user_id: uuid.UUID, demo: AgentDemoService) -> dict[str, Any]:
        """Confirm task execution in PulseCore, persist demo enrollment, normalize UI script."""
        raw = await self._client.execute(self._uid(user_id))
        message = str(raw.get("message", "Готово."))
        status = str(raw.get("status", "ok"))
        backend_req = raw.get("backend_requests")
        if not isinstance(backend_req, list):
            backend_req = []
        await demo.execute_backend_requests(user_id, backend_req)
        frontend_raw = raw.get("frontend_actions")
        frontend_actions = normalize_frontend_actions(frontend_raw)
        return {
            "status": status,
            "message": message,
            "frontend_actions": frontend_actions,
        }

    async def cancel_task(self, user_id: uuid.UUID) -> dict:
        """Cancel pending task."""
        return await self._client.cancel(self._uid(user_id))

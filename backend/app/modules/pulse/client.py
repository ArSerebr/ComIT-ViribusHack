"""HTTP client for PulseCore AI chat API."""

from __future__ import annotations

import httpx

from app.config import get_settings


class PulseCoreClient:
    """Async client for PulseCore API (chat, task, status, history, execute, cancel)."""

    def __init__(self, base_url: str | None = None) -> None:
        self._base = (base_url or get_settings().pulse_core_base_url).rstrip("/")

    async def submit_chat(self, uid: str, message: str) -> str:
        """POST /api/comit/chat. Returns task_id."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self._base}/api/comit/chat",
                params={"uid": uid},
                json={"message": message},
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()
            return str(data["task_id"])

    async def submit_work_plan(
        self,
        uid: str,
        *,
        project_title: str,
        project_description: str,
        project_deadline: str,
        project_id_hint: str = "",
    ) -> str:
        """POST /api/comit/work-plan. Returns task_id."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self._base}/api/comit/work-plan",
                params={"uid": uid},
                json={
                    "project_title": project_title,
                    "project_description": project_description,
                    "project_deadline": project_deadline,
                    "project_id_hint": project_id_hint,
                },
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()
            return str(data["task_id"])

    async def poll_task(self, task_id: str) -> dict:
        """GET /api/task/{task_id}. Returns {status, result?}."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{self._base}/api/task/{task_id}")
            resp.raise_for_status()
            data = resp.json()
            result = {"status": data["status"]}
            if "result" in data:
                result["result"] = data["result"]
            return result

    async def get_status(self, uid: str) -> dict:
        """GET /api/status. Returns {model, status, statusColor, progress}."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self._base}/api/status", params={"uid": uid})
            resp.raise_for_status()
            return resp.json()

    async def get_history(self, uid: str) -> list[dict]:
        """GET /api/history/{uid}. Returns messages list."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self._base}/api/history/{uid}")
            resp.raise_for_status()
            return resp.json()

    async def execute(self, uid: str) -> dict:
        """POST /api/comit/execute. Returns PulseCore JSON (message, frontend_actions, ...)."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self._base}/api/comit/execute",
                params={"uid": uid},
            )
            resp.raise_for_status()
            return resp.json()

    async def cancel(self, uid: str) -> dict:
        """POST /api/comit/cancel. Returns {status, message}."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self._base}/api/comit/cancel",
                params={"uid": uid},
            )
            resp.raise_for_status()
            return resp.json()

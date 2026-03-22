"""Сервис демо-агента: запись на курс и нормализация frontend_actions."""

from __future__ import annotations

import uuid
from typing import Any

from app.modules.agent_demo.models import AgentDemoCourseEnrollment
from app.modules.agent_demo.repository import AgentDemoRepository

DEMO_COURSE_SLUG = "agent-demo-enroll"

ALLOWED_ACTIONS = frozenset(
    {"navigate", "scroll_to", "focus", "type", "click", "wait", "highlight"}
)
ALLOWED_TARGETS = frozenset(
    {
        "enroll-form-root",
        "enroll-email",
        "enroll-phone",
        "enroll-comment",
        "enroll-consent",
        "enroll-submit",
    }
)


def _default_frontend_actions() -> list[dict[str, Any]]:
    """Эталонный сценарий UI для демо-страницы записи на курс."""
    return [
        {
            "action": "navigate",
            "params": {"path": "#/courses/agent-demo-enroll"},
            "delay_after_ms": 1400,
        },
        {"action": "wait", "delay_after_ms": 800},
        {"action": "scroll_to", "target": "enroll-form-root", "delay_after_ms": 1200},
        {"action": "focus", "target": "enroll-email", "delay_after_ms": 600},
        {
            "action": "type",
            "target": "enroll-email",
            "value": "student.demo@comit.local",
            "delay_after_ms": 1400,
        },
        {"action": "focus", "target": "enroll-phone", "delay_after_ms": 600},
        {
            "action": "type",
            "target": "enroll-phone",
            "value": "+79991234567",
            "delay_after_ms": 1200,
        },
        {"action": "focus", "target": "enroll-comment", "delay_after_ms": 600},
        {
            "action": "type",
            "target": "enroll-comment",
            "value": "Хочу пройти программу и собрать портфолио.",
            "delay_after_ms": 1600,
        },
        {"action": "scroll_to", "target": "enroll-consent", "delay_after_ms": 1000},
        {"action": "click", "target": "enroll-consent", "delay_after_ms": 900},
        {"action": "scroll_to", "target": "enroll-submit", "delay_after_ms": 1000},
        {"action": "click", "target": "enroll-submit", "delay_after_ms": 1200},
    ]


def _step_ok(step: dict[str, Any]) -> bool:
    if not isinstance(step, dict):
        return False
    action = step.get("action")
    if action not in ALLOWED_ACTIONS:
        return False
    if action == "navigate":
        params = step.get("params") or {}
        return isinstance(params, dict) and isinstance(params.get("path"), str)
    if action == "wait":
        return True
    if action in ("scroll_to", "focus", "click", "highlight"):
        t = step.get("target")
        return isinstance(t, str) and t in ALLOWED_TARGETS
    if action == "type":
        t = step.get("target")
        v = step.get("value")
        return (
            isinstance(t, str)
            and t in ALLOWED_TARGETS
            and isinstance(v, str)
            and len(v) > 0
        )
    return False


def normalize_frontend_actions(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not raw:
        return _default_frontend_actions()
    out: list[dict[str, Any]] = []
    for step in raw:
        if not _step_ok(step):
            return _default_frontend_actions()
        delay = step.get("delay_after_ms")
        if not isinstance(delay, int) or delay < 200 or delay > 8000:
            return _default_frontend_actions()
        out.append(dict(step))
    return out if out else _default_frontend_actions()


class AgentDemoService:
    def __init__(self, repo: AgentDemoRepository) -> None:
        self._repo = repo

    async def enroll_course(
        self,
        user_id: uuid.UUID,
        *,
        course_slug: str | None = None,
        showcase_item_id: str | None = None,
    ) -> AgentDemoCourseEnrollment:
        slug = (course_slug or DEMO_COURSE_SLUG).strip() or DEMO_COURSE_SLUG
        payload: dict[str, Any] = {}
        if showcase_item_id:
            payload["showcase_item_id"] = showcase_item_id
        return await self._repo.create_enrollment(
            user_id=user_id,
            course_slug=slug,
            payload=payload or None,
        )

    async def execute_backend_requests(
        self,
        user_id: uuid.UUID,
        requests: list[dict[str, Any]] | None,
    ) -> AgentDemoCourseEnrollment | None:
        """Выполняет enroll_course из списка; при пустом списке всё равно создаёт демо-запись."""
        if not requests:
            return await self.enroll_course(user_id)
        did_enroll = False
        last_row: AgentDemoCourseEnrollment | None = None
        for req in requests:
            if not isinstance(req, dict):
                continue
            if req.get("action") != "enroll_course":
                continue
            params = req.get("params") if isinstance(req.get("params"), dict) else {}
            last_row = await self.enroll_course(
                user_id,
                course_slug=params.get("course_slug"),
                showcase_item_id=params.get("showcase_item_id"),
            )
            did_enroll = True
        if not did_enroll:
            return await self.enroll_course(user_id)
        return last_row

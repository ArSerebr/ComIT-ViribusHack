"""Тесты нормализации сценария агента и вызова enroll."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.agent_demo.service import (
    normalize_frontend_actions,
)
from app.modules.pulse.service import PulseService


def test_normalize_frontend_actions_empty_uses_default():
    out = normalize_frontend_actions([])
    assert len(out) >= 10
    assert out[0]["action"] == "navigate"


def test_normalize_frontend_actions_rejects_bad_delay():
    raw = [
        {
            "action": "wait",
            "delay_after_ms": 50,
        }
    ]
    out = normalize_frontend_actions(raw)
    assert out[0]["action"] == "navigate"


def test_normalize_frontend_actions_accepts_valid_chain():
    raw = [
        {
            "action": "navigate",
            "params": {"path": "#/courses/agent-demo-enroll"},
            "delay_after_ms": 800,
        },
        {"action": "wait", "delay_after_ms": 800},
        {
            "action": "scroll_to",
            "target": "enroll-form-root",
            "delay_after_ms": 800,
        },
    ]
    out = normalize_frontend_actions(raw)
    assert len(out) == 3
    assert out[2]["target"] == "enroll-form-root"


@pytest.mark.asyncio
async def test_pulse_execute_task_calls_demo_and_normalizes():
    uid = uuid.uuid4()
    client = MagicMock()
    client.execute = AsyncMock(
        return_value={
            "status": "ok",
            "message": "Готово.",
            "frontend_actions": "not-a-list",
            "backend_requests": [],
        }
    )
    demo = MagicMock()
    demo.execute_backend_requests = AsyncMock(return_value=None)
    svc = PulseService(client)
    result = await svc.execute_task(uid, demo)
    assert result["status"] == "ok"
    assert result["message"] == "Готово."
    assert isinstance(result["frontend_actions"], list)
    assert result["frontend_actions"][0]["action"] == "navigate"
    demo.execute_backend_requests.assert_awaited_once_with(uid, [])

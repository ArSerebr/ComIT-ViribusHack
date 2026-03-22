"""Пайплайн генерации дискретного плана задач проекта (ComIT)."""

from __future__ import annotations

import json
import re
import uuid
from typing import Any

from agents.agent_registry import (
    comit_work_plan_concept,
    comit_work_plan_tasks,
    comit_work_plan_validate,
)
from pipelines.base_pipeline import Pipeline

_VALID_PRIORITIES = frozenset({"must_have", "should_have", "nice_to_have"})
_VALID_DIFFICULTY = frozenset({"low", "medium", "high"})
_VALID_CATEGORIES = frozenset(
    {
        "product",
        "design",
        "frontend",
        "backend",
        "mobile",
        "devops",
        "qa",
        "analytics",
        "ml",
        "other",
    }
)


def _coerce_tasks(raw: Any) -> list[dict[str, Any]]:
    if raw is None:
        return []
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return []
        raw = parsed
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for item in raw:
        if isinstance(item, dict):
            out.append(dict(item))
    return out


def _normalize_deadline(task: dict[str, Any], project_deadline: str) -> str:
    for key in ("deadline_iso", "due_date", "deadline"):
        v = task.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return project_deadline.strip() if isinstance(project_deadline, str) else ""


def normalize_work_plan_tasks(
    tasks: list[dict[str, Any]],
    *,
    project_deadline: str,
    project_id_hint: str = "",
) -> list[dict[str, Any]]:
    """Дополняет и нормализует задачи после LLM."""
    prefix = (project_id_hint or "WP").replace("-", "")[:16] or "WP"
    normalized: list[dict[str, Any]] = []
    for i, t in enumerate(tasks):
        tid = t.get("id")
        if not isinstance(tid, str) or not tid.strip():
            tid = f"{prefix}-T{i + 1:02d}-{uuid.uuid4().hex[:6]}"
        title = t.get("title") if isinstance(t.get("title"), str) else ""
        title = title.strip() or f"Задача {i + 1}"
        desc = t.get("description") if isinstance(t.get("description"), str) else ""
        desc = desc.strip() or title
        skills = t.get("required_skills")
        if not isinstance(skills, list):
            skills = []
        skills = [str(s).strip() for s in skills if str(s).strip()]
        if not skills:
            skills = ["general"]

        cat = t.get("category") if isinstance(t.get("category"), str) else "other"
        cat = cat.strip().lower()
        if cat not in _VALID_CATEGORIES:
            cat = "other"

        diff = t.get("difficulty") if isinstance(t.get("difficulty"), str) else "medium"
        diff = diff.strip().lower()
        if diff not in _VALID_DIFFICULTY:
            diff = "medium"

        prio = t.get("priority") if isinstance(t.get("priority"), str) else "should_have"
        prio = prio.strip().lower()
        if prio not in _VALID_PRIORITIES:
            prio = "should_have"

        hours = t.get("estimated_hours")
        try:
            hours_i = int(hours)
        except (TypeError, ValueError):
            hours_i = 8
        hours_i = max(1, min(hours_i, 200))

        dl = _normalize_deadline(t, project_deadline)
        if not dl:
            dl = "2099-12-31"

        normalized.append(
            {
                "id": tid,
                "title": title,
                "description": desc,
                "required_skills": skills,
                "category": cat,
                "difficulty": diff,
                "estimated_hours": hours_i,
                "priority": prio,
                "deadline_iso": dl,
            }
        )
    return normalized


def split_compound_titles(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Грубое разбиение составных формулировок (и / и также / а также)."""
    pattern = re.compile(r"\s+(?:и|а также|и также)\s+", re.IGNORECASE)
    result: list[dict[str, Any]] = []
    for t in tasks:
        title = t.get("title", "")
        if not isinstance(title, str) or not pattern.search(title):
            result.append(t)
            continue
        parts = [p.strip() for p in pattern.split(title) if p.strip()]
        if len(parts) < 2:
            result.append(t)
            continue
        for j, part in enumerate(parts):
            clone = dict(t)
            clone["title"] = part
            clone["id"] = f"{t['id']}-split{j + 1}"
            clone["description"] = f"{t.get('description', '')} (часть плана: {part})".strip()
            result.append(clone)
    return result


class ComitWorkPlanPipeline(Pipeline):
    """
    Шаги:
    1. ConceptSynthesizer — целевая концепция
    2. DiscreteTaskPlanner — черновик атомарных задач с дедлайнами
    3. WorkPlanValidator — финальный список по критериям
    4. Постобработка: нормализация полей, лёгкое разбиение составных заголовков
    """

    def __init__(self, mode: str = "linear", on_step_start=None):
        super().__init__(
            name=f"ComitWorkPlan_{mode}",
            agents=[],
            on_step_start=on_step_start,
        )

    def run(self, input_data: dict) -> dict:
        memory = {**input_data}
        project_deadline = memory.get("project_deadline") or ""
        project_id_hint = memory.get("project_id_hint") or ""

        if self.on_step_start:
            self.on_step_start("ConceptSynthesizer", 15)
        memory.update(comit_work_plan_concept.run(memory))

        if self.on_step_start:
            self.on_step_start("DiscreteTaskPlanner", 45)
        memory.update(comit_work_plan_tasks.run(memory))

        nc = memory.get("normalized_concept")
        memory["normalized_concept"] = nc if isinstance(nc, str) else json.dumps(nc, ensure_ascii=False)
        td = memory.get("tasks_draft")
        if isinstance(td, (list, dict)):
            memory["tasks_draft"] = json.dumps(td, ensure_ascii=False)
        elif td is None:
            memory["tasks_draft"] = "[]"

        if self.on_step_start:
            self.on_step_start("WorkPlanValidator", 75)
        memory.update(comit_work_plan_validate.run(memory))

        raw_final = memory.get("work_plan_tasks")
        if raw_final is None or raw_final == []:
            raw_final = memory.get("tasks_draft")
        tasks = _coerce_tasks(raw_final)
        tasks = split_compound_titles(
            normalize_work_plan_tasks(
                tasks,
                project_deadline=str(project_deadline),
                project_id_hint=str(project_id_hint),
            )
        )
        memory["work_plan_tasks"] = tasks

        if self.on_step_start:
            self.on_step_start("PulsAR", 100)

        self._meta["status"] = "success"
        return memory

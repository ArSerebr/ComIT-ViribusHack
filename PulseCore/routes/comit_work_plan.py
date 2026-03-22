"""Генерация плана задач проекта через PulseCore."""

from __future__ import annotations

import logging
from fastapi import APIRouter, BackgroundTasks, Query

from pipelines.comit_work_plan_pipeline import ComitWorkPlanPipeline
from state.state_manager import create_task, set_agent_status, update_task

router = APIRouter()


def process_work_plan(task_id: str, uid: str | None, payload: dict) -> None:
    debug: list[dict] = []
    try:
        if uid:
            set_agent_status(uid, "ConceptSynthesizer", 5)

        memory_in = {
            "project_title": (payload.get("project_title") or "").strip(),
            "project_description": (payload.get("project_description") or "").strip(),
            "project_deadline": (payload.get("project_deadline") or "").strip(),
            "project_id_hint": (payload.get("project_id_hint") or "").strip(),
        }

        pipeline = ComitWorkPlanPipeline(
            mode="linear",
            on_step_start=lambda name, p: set_agent_status(uid, name, p) if uid else None,
        )
        final_memory = pipeline.run(memory_in)
        debug.append(
            {
                "agent": "ComitWorkPlanPipeline",
                "model": "pipeline",
                "input": memory_in,
                "output_keys": list(final_memory.keys()),
            }
        )

        tasks = final_memory.get("work_plan_tasks") or []
        result = {
            "role": "work_plan",
            "content": {
                "normalized_concept": final_memory.get("normalized_concept"),
                "plan_summary": final_memory.get("plan_summary"),
                "work_plan_tasks": tasks,
            },
            "buttons": [],
        }
        update_task(task_id, "READY", {**result, "_debug": debug})
        if uid:
            set_agent_status(uid, "READY", 100)
    except Exception as e:
        logging.error("Error in process_work_plan: %s", e, exc_info=True)
        update_task(
            task_id,
            "FAILED",
            {"error": str(e), "_debug": debug},
        )


@router.post("/api/comit/work-plan")
def post_work_plan(
    payload: dict,
    background_tasks: BackgroundTasks,
    uid: str | None = Query(default=None),
):
    """
    Тело: project_title, project_description, project_deadline (строка, напр. YYYY-MM-DD),
    опционально project_id_hint для префиксов id задач.
    """
    effective_uid = uid or "anonymous"
    task_id = create_task(effective_uid)
    background_tasks.add_task(process_work_plan, task_id, uid, payload)
    return {"task_id": task_id}

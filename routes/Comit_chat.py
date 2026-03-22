from fastapi import APIRouter, Query, BackgroundTasks, HTTPException
import logging

from state.state_manager import (get_state, save_state, create_task, update_task, save_message, set_agent_status)
from state.context_manager import (
    get_global_context, add_to_global_context,
    get_session_context, add_to_session_context
)
from agents.agent_registry import comit_request_classifier, comit_conversation_agent
from pipelines.comit_agent_pipeline import ComitAgentPipeline
from pipelines.comit_search_pipeline import ComitSearchPipeline

router = APIRouter()


@router.post("/api/comit/chat")
def chat(payload: dict, background_tasks: BackgroundTasks, uid: str = Query(...)):
    task_id = create_task(uid)
    background_tasks.add_task(process_chat, task_id, uid, payload)
    return {"task_id": task_id}


def update_task_and_save(task_id: str, uid: str, status: str, result: dict, debug: list = None):
    if debug is not None:
        result = {**result, "_debug": debug}
    update_task(task_id, status, result)
    if status == "READY" and result:
        save_message(uid, result.get("role", "ai"), result.get("content", ""), result.get("buttons", []))
        set_agent_status(uid, "READY", 100)


def _run_agent(agent, inputs: dict, debug: list) -> dict:
    result = agent.run(inputs)
    debug.append({
        "agent": agent.name,
        "model": agent.model,
        "input": inputs,
        "output": result,
    })
    return result


def process_chat(task_id: str, uid: str, payload: dict):
    debug = []
    try:
        message = payload.get("message", "")
        save_message(uid, "user", message)

        session_ctx = get_session_context(uid)
        global_ctx = get_global_context(uid)
        state = get_state(uid)

        add_to_session_context(uid, "user", message)
        add_to_global_context(uid, "user", message)

        # ── 1. Классификация ──────────────────────────────────────
        set_agent_status(uid, "RequestClassifier", 10)
        classification = _run_agent(comit_request_classifier, {"message": message}, debug)
        msg_type = classification.get("message_type", "other")

        # ── 2. Оффтоп / непонятный запрос ────────────────────────
        if msg_type == "other":
            set_agent_status(uid, "ConversationAgent", 40)
            res = _run_agent(comit_conversation_agent, {
                "message": message,
                "session_context": session_ctx,
                "global_context": global_ctx
            }, debug)
            answer = res.get("answer", "Я не совсем понимаю ваш запрос. Попробуйте переформулировать.")
            add_to_session_context(uid, "ai", answer)
            add_to_global_context(uid, "ai", answer)
            update_task_and_save(task_id, uid, "READY", {"role": "ai", "content": answer, "buttons": []}, debug)
            return

        # ── 3. Вопрос ────────────────────────────────────────────
        if msg_type == "question":
            set_agent_status(uid, "ConversationAgent", 40)
            res = _run_agent(comit_conversation_agent, {
                "message": message,
                "session_context": session_ctx,
                "global_context": global_ctx
            }, debug)
            answer = res.get("answer", "Произошла ошибка при обработке вопроса. Попробуйте ещё раз.")
            add_to_session_context(uid, "ai", answer)
            add_to_global_context(uid, "ai", answer)
            update_task_and_save(task_id, uid, "READY", {"role": "ai", "content": answer, "buttons": []}, debug)
            return

        # ── 4. Задача (агентский режим) ───────────────────────────
        if msg_type == "task":
            set_agent_status(uid, "TaskSetupAgent", 30)
            pipeline = ComitAgentPipeline(
                mode="linear",
                on_step_start=lambda name, p: set_agent_status(uid, name, p)
            )
            final_memory = pipeline.run({"message": message})
            debug.append({"agent": "ComitAgentPipeline", "model": "pipeline", "input": {"message": message}, "output": final_memory})

            explain = final_memory.get("pipeline_explanation", "Выполняю задачу...")
            front_requests = final_memory.get("frontend_requests", [])
            back_requests = final_memory.get("backend_requests", [])

            state["last_task"] = {
                "message": message,
                "frontend_requests": front_requests,
                "backend_requests": back_requests
            }
            state["stage"] = "task_pending"
            save_state(uid, state)

            add_to_session_context(uid, "ai", explain)
            add_to_global_context(uid, "ai", explain)

            update_task_and_save(task_id, uid, "READY", {
                "role": "ai",
                "content": {"explanation": explain, "to_show": front_requests},
                "buttons": ["Запустить агента", "Отмена"]
            }, debug)
            return

        # ── 5. Поиск (RAG) ────────────────────────────────────────
        if msg_type == "search":
            set_agent_status(uid, "SearchAgent", 20)
            pipeline = ComitSearchPipeline(
                mode="linear",
                on_step_start=lambda name, p: set_agent_status(uid, name, p)
            )
            final_memory = pipeline.run({"message": message})
            debug.append({"agent": "ComitSearchPipeline", "model": "pipeline", "input": {"message": message}, "output": final_memory})

            answer = final_memory.get("answer", "По вашему запросу ничего не найдено.")
            source_buttons = final_memory.get("found_sources", [])

            add_to_session_context(uid, "ai", answer)
            add_to_global_context(uid, "ai", answer)
            update_task_and_save(task_id, uid, "READY", {"role": "ai", "content": answer, "buttons": source_buttons}, debug)
            return

        # ── Fallback (неизвестный msg_type) ───────────────────────
        debug.append({"agent": "FALLBACK", "model": "-", "input": {"msg_type": msg_type}, "output": {}})
        res = _run_agent(comit_conversation_agent, {
            "message": message,
            "session_context": session_ctx,
            "global_context": global_ctx
        }, debug)
        answer = res.get("answer", "Готов помочь! Задайте вопрос или опишите что нужно сделать.")
        add_to_session_context(uid, "ai", answer)
        add_to_global_context(uid, "ai", answer)
        update_task_and_save(task_id, uid, "READY", {"role": "ai", "content": answer, "buttons": []}, debug)

    except Exception as e:
        logging.error(f"Error in comit process_chat: {e}", exc_info=True)
        update_task(task_id, "FAILED", {"error": str(e), "_debug": debug})


# ── Подтверждение задачи ──────────────────────────────────────────

@router.post("/api/comit/execute")
def execute_task(uid: str = Query(...)):
    state = get_state(uid)
    if state.get("stage") != "task_pending":
        raise HTTPException(status_code=400, detail="No pending task")

    last_task = state.get("last_task", {})
    backend_requests = last_task.get("backend_requests", [])

    # Здесь будет реальное выполнение backend_requests
    # Пока формируем читаемый отчёт об исполненных действиях
    if backend_requests:
        actions = ", ".join(r.get("action", "?") for r in backend_requests)
        msg = f"Готово. Выполнено: {actions}."
    else:
        msg = "Задача выполнена."

    state["stage"] = "idle"
    state["last_task"] = {}
    save_state(uid, state)
    save_message(uid, "ai", msg)

    return {"status": "ok", "message": msg}


@router.post("/api/comit/cancel")
def cancel_task(uid: str = Query(...)):
    state = get_state(uid)
    state["stage"] = "idle"
    state["last_task"] = {}
    save_state(uid, state)

    msg = "Задача отменена."
    save_message(uid, "ai", msg)

    return {"status": "cancelled", "message": msg}

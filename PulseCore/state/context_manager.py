"""
Context Manager для ComIT AI-ассистента.

- Глобальный контекст (global): персистентный в MongoDB, ограничен по размеру,
  сжимается через LLM когда превышает лимит.
- Сессионный контекст (session): in-memory, хранит сообщения текущей сессии.
"""

from datetime import datetime
from typing import List
from db.mongo import states
from services.llm import llm

# ─── Настройки ────────────────────────────────────────────────
MAX_GLOBAL_MESSAGES = 20      # После этого значения — сжатие
COMPRESS_KEEP = 5             # Сколько последних сообщений оставить после сжатия
MAX_SESSION_MESSAGES = 10     # Размер сессионного окна
MAX_CONTENT_LEN = 600         # Обрезка отдельного сообщения (символов)

# ─── Сессионный контекст (in-memory) ─────────────────────────
_session_contexts: dict = {}


def get_session_context(uid: str) -> str:
    """Возвращает историю текущей сессии как строку для промпта."""
    messages = _session_contexts.get(uid, [])
    if not messages:
        return ""
    lines = []
    for m in messages:
        label = "Студент" if m["role"] == "user" else "Ассистент"
        lines.append(f"{label}: {m['content']}")
    return "\n".join(lines)


def add_to_session_context(uid: str, role: str, content: str):
    """Добавляет сообщение в сессионный контекст."""
    if uid not in _session_contexts:
        _session_contexts[uid] = []
    _session_contexts[uid].append({
        "role": role,
        "content": content[:MAX_CONTENT_LEN]
    })
    # Держим только последние N сообщений
    if len(_session_contexts[uid]) > MAX_SESSION_MESSAGES:
        _session_contexts[uid] = _session_contexts[uid][-MAX_SESSION_MESSAGES:]


def clear_session_context(uid: str):
    """Очищает сессионный контекст пользователя."""
    _session_contexts.pop(uid, None)


# ─── Глобальный контекст (MongoDB) ───────────────────────────

def get_global_context(uid: str) -> str:
    """Возвращает глобальный контекст как строку для промпта."""
    doc = states.find_one({"uid": uid}, {"global_context": 1}) or {}
    ctx = doc.get("global_context", {})
    if not ctx:
        return ""

    lines = []
    summary = ctx.get("summary", "")
    if summary:
        lines.append(f"[Сводка предыдущих сессий]: {summary}")
    for m in ctx.get("messages", []):
        label = "Студент" if m["role"] == "user" else "Ассистент"
        lines.append(f"{label}: {m['content']}")
    return "\n".join(lines)


def add_to_global_context(uid: str, role: str, content: str):
    """
    Добавляет сообщение в глобальный контекст.
    При превышении MAX_GLOBAL_MESSAGES — сжимает старые сообщения.
    """
    doc = states.find_one({"uid": uid}, {"global_context": 1}) or {}
    ctx = doc.get("global_context", {"summary": "", "messages": []})

    ctx["messages"].append({
        "role": role,
        "content": content[:MAX_CONTENT_LEN],
        "ts": datetime.utcnow().isoformat()
    })

    if len(ctx["messages"]) > MAX_GLOBAL_MESSAGES:
        ctx = _compress_global_context(ctx)

    states.update_one(
        {"uid": uid},
        {"$set": {"global_context": ctx}},
        upsert=True
    )


def _compress_global_context(ctx: dict) -> dict:
    """
    Сжимает старые сообщения глобального контекста через LLM в краткую сводку.
    Оставляет последние COMPRESS_KEEP сообщений нетронутыми.
    """
    to_compress: List[dict] = ctx["messages"][:-COMPRESS_KEEP]
    keep: List[dict] = ctx["messages"][-COMPRESS_KEEP:]
    old_summary = ctx.get("summary", "")

    # Собираем текст для сжатия
    parts = []
    if old_summary:
        parts.append(f"Предыдущая сводка: {old_summary}")
    for m in to_compress:
        label = "Студент" if m["role"] == "user" else "Ассистент"
        parts.append(f"{label}: {m['content']}")

    compress_prompt = (
        "Сожми историю диалога в краткую сводку (3-5 предложений).\n"
        "Сохрани важные факты: курсы студента, его запросы, ключевые ответы.\n"
        "Верни только текст сводки без JSON и форматирования.\n\n"
        + "\n".join(parts)
    )

    try:
        new_summary = llm(compress_prompt, "gpt_nano")
        # Если LLM вернул "0" или пустую строку — оставляем старую сводку
        if not new_summary or new_summary == "0":
            new_summary = old_summary
    except Exception:
        new_summary = old_summary

    return {
        "summary": new_summary,
        "messages": keep
    }

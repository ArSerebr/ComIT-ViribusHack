"""
RAG-заглушка для ComIT.

Возвращает тестовые данные вместо реального поиска по MongoDB.
Когда база будет готова — заменить тело rag_retrieve на реальный поиск.

rag_retrieve возвращает dict:
  {
    "chunks":  [str, ...]   — текстовые чанки для LLM
    "sources": [{"label": str, "type": str, "url": str}, ...]  — для кнопок
  }
"""

STUB_DATA = [
    {
        "type": "course",
        "title": "Введение в машинное обучение",
        "content": "Базовый курс по ML: линейная регрессия, классификация, кластеризация. Преподаватель: Иванов А.С. Длительность: 8 недель.",
        "tags": ["ml", "машинное обучение", "python", "data science"],
        "url": "/courses/intro-ml"
    },
    {
        "type": "event",
        "title": "Хакатон ML Weekend #3",
        "content": "Хакатон по машинному обучению. Даты: 22-23 марта 2026 (суббота-воскресенье). Тема: предсказание оттока клиентов. Призовой фонд: 50 000 руб. Регистрация открыта.",
        "tags": ["хакатон", "ml", "выходные", "соревнование"],
        "url": "/events/hackathon-ml-3"
    },
    {
        "type": "course",
        "title": "Deep Learning с нуля",
        "content": "Продвинутый курс по нейросетям: CNN, RNN, трансформеры. Требования: знание основ ML. Преподаватель: Петрова М.В.",
        "tags": ["deep learning", "нейросети", "pytorch", "ml"],
        "url": "/courses/deep-learning"
    },
    {
        "type": "assignment",
        "title": "Задание 3: Классификация текстов",
        "content": "Реализовать классификатор отзывов на основе TF-IDF и логистической регрессии. Дедлайн: 30 марта 2026.",
        "tags": ["nlp", "классификация", "задание"],
        "url": "/assignments/3"
    },
]

_TYPE_LABELS = {
    "course":     "Курс",
    "event":      "Событие",
    "assignment": "Задание",
    "article":    "Статья",
    "teacher":    "Преподаватель",
}


def rag_retrieve(query: str, limit: int = 5) -> dict:
    """
    Заглушка: возвращает тестовые материалы, отфильтрованные по ключевым словам запроса.
    Возвращает {"chunks": [...], "sources": [...]}.
    """
    if not query or not query.strip():
        return {"chunks": [], "sources": []}

    query_lower = query.lower()
    scored = []
    for doc in STUB_DATA:
        score = 0
        searchable = (
            doc.get("title", "") + " " +
            doc.get("content", "") + " " +
            " ".join(doc.get("tags", []))
        ).lower()
        for word in query_lower.split():
            if len(word) > 2 and word in searchable:
                score += 1
        if score > 0:
            scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_docs = [doc for _, doc in scored[:limit]]

    return {
        "chunks": _format_chunks(top_docs),
        "sources": _format_sources(top_docs),
    }


def _format_chunks(docs: list) -> list:
    chunks = []
    for doc in docs:
        parts = []
        if doc.get("type"):
            parts.append(f"[{doc['type']}]")
        if doc.get("title"):
            parts.append(doc["title"])
        if doc.get("content"):
            parts.append(doc["content"][:800])
        if parts:
            chunks.append(" | ".join(parts))
    return chunks


def _format_sources(docs: list) -> list:
    sources = []
    for doc in docs:
        title = doc.get("title", "")
        doc_type = doc.get("type", "")
        url = doc.get("url", "")
        if not title or not url:
            continue
        type_label = _TYPE_LABELS.get(doc_type, doc_type)
        sources.append({
            "label": f"{type_label}: {title}",
            "type": doc_type,
            "url": url,
        })
    return sources

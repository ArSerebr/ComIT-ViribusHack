from pipelines.base_pipeline import Pipeline
from agents.agent_registry import comit_search, comit_search_results
from services.rag_search import rag_retrieve


class ComitSearchPipeline(Pipeline):
    """
    RAG-пайплайн поиска по платформе ComIT.

    Шаги:
    1. comit_search     — переформулирует запрос в поисковые ключевые слова
    2. rag_retrieve     — извлекает релевантные материалы из MongoDB
    3. comit_search_results — формирует ответ студенту на основе найденных материалов
    """

    def __init__(self, mode="linear", on_step_start=None):
        self.mode = mode
        # Агенты не передаём в base (run переопределён полностью)
        super().__init__(
            name=f"ComitSearch_{mode}",
            agents=[],
            on_step_start=on_step_start
        )

    def run(self, input_data: dict) -> dict:
        memory = {**input_data}

        # ── Шаг 1: Переформулировать запрос ──────────────────────
        if self.on_step_start:
            self.on_step_start("SearchAgent", 20)

        query_result = comit_search.run(memory)
        memory.update(query_result)

        # ── Шаг 2: RAG-извлечение из MongoDB ─────────────────────
        if self.on_step_start:
            self.on_step_start("SearchAgent", 50)

        search_query = memory.get("search_query") or memory.get("message", "")
        rag_result = rag_retrieve(search_query)

        chunks = rag_result.get("chunks", [])
        memory["found_sources"] = rag_result.get("sources", [])

        if chunks:
            memory["found_items"] = "\n---\n".join(chunks)
        else:
            memory["found_items"] = "Материалы по данному запросу не найдены."

        # ── Шаг 3: Формирование ответа ────────────────────────────
        if self.on_step_start:
            self.on_step_start("SearchResultsAgent", 80)

        result = comit_search_results.run(memory)
        memory.update(result)

        if self.on_step_start:
            self.on_step_start("PulsAR", 100)

        return memory

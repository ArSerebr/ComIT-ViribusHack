from agents.base_agent import Agent

# ── ComIT АГЕНТЫ ──────────────────────────────────────────────

# Классификатор типа запроса (question / task / search / other)
comit_request_classifier = Agent(
    name="RequestClassifier",
    model="gpt_nano",
    use_context=False,
    input_fields=["message"],
    output_fields=["message_type"],
    system_prompt_key="comit_request_classifier"
)

# Агент общения со студентами
comit_conversation_agent = Agent(
    name="ConversationAgent",
    model="deepseek",
    use_context=True,
    input_fields=["message", "session_context", "global_context"],
    output_fields=["answer"],
    system_prompt_key="comit_conversation_agent"
)

# Агент формулировки ТЗ задачи
comit_task_setup_agent = Agent(
    name="TaskSetupAgent",
    model="gpt_nano",
    use_context=False,
    input_fields=["message"],
    output_fields=["task_description"],
    system_prompt_key="comit_task_setup_agent"
)

# Агент выполнения действий на платформе
comit_user_agent = Agent(
    name="UserAgent",
    model="gemini",
    use_context=False,
    input_fields=["task_description"],
    output_fields=["backend_requests", "frontend_requests"],
    system_prompt_key="comit_user_agent"
)

# Агент объяснения хода выполнения задачи
comit_planner_agent = Agent(
    name="PlannerAgent",
    model="gpt_nano",
    use_context=False,
    input_fields=["frontend_request"],
    output_fields=["pipeline_explanation"],
    system_prompt_key="comit_planner_agent"
)

# Агент формирования поискового запроса
comit_search = Agent(
    name="SearchAgent",
    model="gpt_nano",
    use_context=True,
    input_fields=["message"],
    output_fields=["found_items"],
    system_prompt_key="comit_search"
)

# Агент обработки результатов поиска
comit_search_results = Agent(
    name="SearchResultsAgent",
    model="deepseek",
    use_context=False,
    input_fields=["message", "found_items"],
    output_fields=["answer"],
    system_prompt_key="comit_search_results"
)

AGENTS_METADATA = {
    "RequestClassifier": {
        "color": "#2485B6",
        "text": "Анализирую запрос"
    },
    "ConversationAgent": {
        "color": "#4caf50",
        "text": "Отвечаю на вопрос"
    },
    "TaskSetupAgent": {
        "color": "#2196f3",
        "text": "Формулирую задачу"
    },
    "UserAgent": {
        "color": "#9c27b0",
        "text": "Выполняю действие"
    },
    "PlannerAgent": {
        "color": "#ff9800",
        "text": "Планирую шаги"
    },
    "SearchAgent": {
        "color": "#2485B6",
        "text": "Ищу по платформе"
    },
    "SearchResultsAgent": {
        "color": "#4caf50",
        "text": "Обрабатываю результаты"
    },
    "PulsAR": {
        "color": "#4caf50",
        "text": "Печатает..."
    },
}

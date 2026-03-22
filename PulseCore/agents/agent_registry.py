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
    input_fields=["task_description", "frontend_requests"],
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

comit_work_plan_concept = Agent(
    name="ConceptSynthesizer",
    model="gpt_nano",
    use_context=False,
    input_fields=["project_title", "project_description", "project_deadline"],
    output_fields=["normalized_concept"],
    system_prompt_key="comit_work_plan_concept",
)

comit_work_plan_tasks = Agent(
    name="DiscreteTaskPlanner",
    model="gemini",
    use_context=False,
    input_fields=["normalized_concept", "project_deadline"],
    output_fields=["tasks_draft"],
    system_prompt_key="comit_work_plan_tasks",
)

comit_work_plan_validate = Agent(
    name="WorkPlanValidator",
    model="gpt_nano",
    use_context=False,
    input_fields=["normalized_concept", "tasks_draft"],
    output_fields=["work_plan_tasks", "plan_summary"],
    system_prompt_key="comit_work_plan_validate",
)

AGENTS_METADATA = {
    "RequestClassifier": {
        "color": "#2444B6",
        "text": "Анализирую запрос"
    },
    "ConversationAgent": {
        "color": "#aa42bd",
        "text": "Вызываю LLM"
    },
    "TaskSetupAgent": {
        "color": "#67c0d8",
        "text": "Формулирую задачу"
    },
    "UserAgent": {
        "color": "#743bc5",
        "text": "Выполняю задание"
    },
    "PlannerAgent": {
        "color": "#ff9800",
        "text": "Записываю план"
    },
    "SearchAgent": {
        "color": "#C62741",
        "text": "Выполняю поиск на платформе"
    },
    "SearchResultsAgent": {
        "color": "#C5520F",
        "text": "Обрабатываю результаты"
    },
    "ConceptSynthesizer": {
        "color": "#1565c0",
        "text": "Формирую концепцию проекта"
    },
    "DiscreteTaskPlanner": {
        "color": "#6a1b9a",
        "text": "Декомпозирую задачи"
    },
    "WorkPlanValidator": {
        "color": "#2e7d32",
        "text": "Проверяю план"
    },
    "PulsAR": {
        "color": "#4caf50",
        "text": "Печатает..."
    },
    "READY": {
        "color": "#4caf50",
        "text": "Печатает..."
    }
}

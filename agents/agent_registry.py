from agents.base_agent import Agent

# Классификатор входящих сообщений
classifier_agent = Agent(
    name="intent_classifier",
    model="deepseek",
    use_context=False,
    input_fields=["message"],
    output_fields=["type", "idea_id"],
    system_prompt_key="intent_classifier"
)

# Расширитель идеи (генератор 3-х проектов)
idea_expander_agent = Agent(
    name="IdeaExpander",
    model="gemini",
    use_context=False,
    input_fields=["message"],
    output_fields=["ideas"],
    system_prompt_key="idea_expander"
)

# Критик проектов
idea_critic_agent = Agent(
    name="IdeaCritic",
    model="deepseek",
    use_context=False,
    input_fields=["ideas"],
    output_fields=["criticisms"],
    system_prompt_key="idea_critic"
)

# Улучшатель проектов на основе критики
idea_refiner_agent = Agent(
    name="IdeaRefiner",
    model="gemini",
    use_context=False,
    input_fields=["ideas", "criticisms"],
    output_fields=["final_ideas"],
    system_prompt_key="idea_refiner"
)

# Селектор лучших идей
idea_selector_agent = Agent(
    name="IdeaSelector",
    model="gpt_nano",
    use_context=False,
    input_fields=["final_ideas"],
    output_fields=["final_ideas"],
    system_prompt_key="idea_selector"
)

# Агент для свободного общения
conversation_agent = Agent(
    name="ConversationAgent",
    model="gpt_nano",
    use_context=True,
    input_fields=["message", "state"],
    output_fields=["reply"],
    system_prompt_key="conversation_agent"
)

# Агент для доработки одной идеи
one_idea_refiner_agent = Agent(
    name="OneIdeaRefiner",
    model="gemini",
    use_context=True,
    input_fields=["idea", "message"],
    output_fields=["final_idea"],
    system_prompt_key="one_idea_refiner"
)

AGENTS_METADATA = {
    "Classifier": {
        "color": "#2485B6",
        "text": "Анализирую запрос"
    },
    "IdeaExpander": {
        "color": "#2196f3",
        "text": "Генерирую идеи"
    },
    "IdeaCritic": {
        "color": "#ff9800",
        "text": "Ищу слабые места"
    },
    "IdeaRefiner": {
        "color": "#9c27b0",
        "text": "Дорабатываю идеи"
    },
    "IdeaSelector": {
        "color": "#4caf50",
        "text": "Отбираю лучшие идеи"
    },
    "PulsAR": {
        "color": "#4caf50",
        "text": "Печатает..."
    }
}

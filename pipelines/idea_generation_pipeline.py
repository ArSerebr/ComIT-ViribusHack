from pipelines.base_pipeline import Pipeline
from agents.agent_registry import (
    idea_expander_agent, 
    idea_critic_agent, 
    idea_refiner_agent, 
    idea_selector_agent
)

class IdeaGenerationPipeline(Pipeline):
    def __init__(self, mode="linear", on_step_start=None):
        self.mode = mode
        if mode == "arena":
            # Арена - Сгенерировать параллельно по три идеи (всего 6) 
            # -> найти слабые места (1 общий агент) 
            # -> доработать параллельно по три идеи (2 агента) 
            # -> отобрать три лучших -> вернуть
            agents = [
                [idea_expander_agent, idea_expander_agent], # Параллельно 2 по 3 = 6 идей
                idea_critic_agent,                          # 1 общий критик
                [idea_refiner_agent, idea_refiner_agent],   # Параллельно доработка
                idea_selector_agent                         # Отбор 3-х лучших
            ]
        else:
            # Линейная - Сгенерить три проекта, провести критику для трех проектов, 
            # доработать проекты в соответствии с критикой, вернуть готовые проекты для выбора
            agents = [
                idea_expander_agent,
                idea_critic_agent,
                idea_refiner_agent
            ]
        
        super().__init__(name=f"IdeaGeneration_{mode}", agents=agents, on_step_start=on_step_start)

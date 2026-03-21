from pipelines.base_pipeline import Pipeline
from agents.agent_registry import (
    comit_task_setup_agent,
    comit_user_agent,
    comit_planner_agent
)

class ComitAgentPipeline(Pipeline):
    def __init__(self, mode="linear", on_step_start=None):
        self.mode = mode
        agents = [
                comit_task_setup_agent,
                comit_user_agent,
                comit_planner_agent
            ]
        
        super().__init__(name=f"IdeaGeneration_{mode}", agents=agents, on_step_start=on_step_start)
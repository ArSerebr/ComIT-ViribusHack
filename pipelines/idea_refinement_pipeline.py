from pipelines.base_pipeline import Pipeline
from agents.agent_registry import one_idea_refiner_agent

class IdeaRefinementPipeline(Pipeline):
    def __init__(self, on_step_start=None):
        super().__init__(name="IdeaRefinement", agents=[one_idea_refiner_agent], on_step_start=on_step_start)

"""API роуты."""

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from app.services.runner import run_parse_task

router = APIRouter(prefix="/api", tags=["parser"])


class HealthResponse(BaseModel):
    status: str = "ok"


class TriggerResponse(BaseModel):
    status: str
    message: str


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check для load balancer / Docker."""
    return HealthResponse()


@router.post("/parse/trigger", response_model=TriggerResponse)
async def trigger_parse(background_tasks: BackgroundTasks) -> TriggerResponse:
    """Запустить парсинг в фоне."""
    background_tasks.add_task(run_parse_task)
    return TriggerResponse(
        status="started",
        message="Парсинг запущен в фоновом режиме",
    )

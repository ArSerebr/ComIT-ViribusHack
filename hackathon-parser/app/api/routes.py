"""API роуты."""

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from app.news.runner import run_news_task
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
    """Запустить парсинг хакатонов в фоне."""
    background_tasks.add_task(run_parse_task)
    return TriggerResponse(
        status="started",
        message="Парсинг хакатонов запущен в фоне",
    )


@router.post("/parse/trigger-news", response_model=TriggerResponse)
async def trigger_news(background_tasks: BackgroundTasks) -> TriggerResponse:
    """Запустить сбор IT-новостей (RSS) в фоне."""
    background_tasks.add_task(run_news_task)
    return TriggerResponse(
        status="started",
        message="Сбор IT-новостей запущен в фоне",
    )

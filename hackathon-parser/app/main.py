"""Content Parser — хакатоны + IT-новости (RSS). FastAPI + APScheduler."""

from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from app.api.routes import router
from app.config import get_settings
from app.news.runner import run_news_task
from app.services.runner import run_parse_task

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ComIT Content Parser",
    version="1.1.0",
    description="Хакатоны (hacklist, cups, Networkly) и IT-новости (RSS: Хабр, VC.ru, iXBT).",
)
app.include_router(router)


@app.get("/health")
async def root_health() -> dict[str, str]:
    """Health check для Docker / load balancer."""
    return {"status": "ok"}


scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def startup() -> None:
    settings = get_settings()
    interval_hours = settings.parse_interval_hours
    news_hours = settings.news_parse_interval_hours
    scheduler.add_job(run_parse_task, "interval", hours=interval_hours, id="parse_hackathons")
    scheduler.add_job(run_news_task, "interval", hours=news_hours, id="parse_it_news")
    scheduler.start()
    logger.info(
        "Scheduler: hackathons every %d h, IT news every %d h",
        interval_hours,
        news_hours,
    )
    await run_parse_task()
    await run_news_task()


@app.on_event("shutdown")
async def shutdown() -> None:
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")

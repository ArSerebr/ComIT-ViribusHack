"""Hackathon Parser Service — FastAPI + APScheduler."""

from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from app.api.routes import router
from app.config import get_settings
from app.services.runner import run_parse_task

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Hackathon Parser",
    version="1.0.0",
    description="Сервис парсинга хакатонов с hacklist.ru, cups.online и др.",
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
    scheduler.add_job(run_parse_task, "interval", hours=interval_hours, id="parse_hackathons")
    scheduler.start()
    logger.info("Scheduler started, parse every %d hour(s)", interval_hours)
    # Запуск при старте
    await run_parse_task()


@app.on_event("shutdown")
async def shutdown() -> None:
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")

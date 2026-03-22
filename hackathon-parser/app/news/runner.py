"""Запуск сбора новостей."""

from __future__ import annotations

import logging

from app.db.session import async_session_maker
from app.news.rss import fetch_all_rss
from app.news.saver import upsert_it_news

logger = logging.getLogger(__name__)


async def run_news_task() -> None:
    try:
        items = await fetch_all_rss()
    except Exception as e:
        logger.exception("RSS fetch failed: %s", e)
        return

    if not items:
        logger.warning("No IT news items fetched")
        return

    async with async_session_maker() as session:
        n = await upsert_it_news(session, items)
        logger.info("Saved %d IT news items", n)

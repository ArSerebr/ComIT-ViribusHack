"""Запуск парсинга всех источников."""

from __future__ import annotations

import logging

from app.db.session import async_session_maker
from app.parsers import get_parsers
from app.parsers.base import RawHackathon
from app.services.saver import upsert_hackathons

logger = logging.getLogger(__name__)


async def run_parse_task() -> None:
    """Запустить парсинг всех источников и сохранить в БД."""
    all_items: list[RawHackathon] = []
    for parser in get_parsers():
        try:
            items = await parser.fetch_all()
            if items:
                all_items.extend(items)
                logger.info("Parsed %d from %s", len(items), parser.source_name)
            else:
                logger.warning("No items from %s", parser.source_name)
        except Exception as e:
            logger.exception("Parser %s failed: %s", parser.source_name, e)

    if all_items:
        async with async_session_maker() as session:
            total = await upsert_hackathons(session, all_items)
            logger.info("Saved %d hackathons to DB", total)
    else:
        logger.warning("No items to save")

"""Загрузка IT-новостей из публичных RSS."""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

import feedparser
import httpx

from app.news.models_dataclass import RawItNews

logger = logging.getLogger(__name__)

# Публичные RSS (без ключа API)
RSS_FEEDS: list[tuple[str, str]] = [
    ("habr", "https://habr.com/ru/rss/all/all/?fl=ru"),
    ("vc_ru", "https://vc.ru/rss"),
    ("ixbt", "https://www.ixbt.com/export/news.rss"),
]


def _entry_published(entry: Any) -> datetime | None:
    if getattr(entry, "published_parsed", None):
        try:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        except (TypeError, ValueError):
            pass
    if getattr(entry, "published", None):
        try:
            dt = parsedate_to_datetime(entry.published)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (TypeError, ValueError):
            pass
    return None


def _entry_summary(entry: Any) -> str | None:
    if getattr(entry, "summary", None):
        s = entry.summary
        if isinstance(s, str) and s.strip():
            return s[:8000]
    if getattr(entry, "description", None):
        d = entry.description
        if isinstance(d, str) and d.strip():
            return d[:8000]
    return None


async def fetch_all_rss(max_per_feed: int = 80) -> list[RawItNews]:
    """Скачать и разобрать все настроенные ленты."""
    out: list[RawItNews] = []
    headers = {"User-Agent": "ComIT-NewsParser/1.0"}

    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=45.0,
        headers=headers,
    ) as client:
        for source, url in RSS_FEEDS:
            try:
                resp = await client.get(url)
                resp.raise_for_status()
            except Exception as e:
                logger.warning("RSS fetch failed %s: %s", url, e)
                continue

            parsed = feedparser.parse(resp.text)
            if parsed.bozo and not parsed.entries:
                logger.warning("RSS parse error for %s: %s", url, getattr(parsed, "bozo_exception", None))

            for entry in parsed.entries[:max_per_feed]:
                link = getattr(entry, "link", None) or ""
                if not link or not isinstance(link, str):
                    continue
                title = getattr(entry, "title", None) or ""
                if isinstance(title, str):
                    title = title.strip()
                if not title:
                    continue

                ext = hashlib.sha256(link.encode("utf-8")).hexdigest()[:32]
                pub = _entry_published(entry)
                summ = _entry_summary(entry)

                out.append(
                    RawItNews(
                        external_id=ext,
                        source=source,
                        title=title[:2000],
                        summary=summ,
                        url=link[:2048],
                        published_at=pub,
                    )
                )

    return out

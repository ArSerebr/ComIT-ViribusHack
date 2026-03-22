"""Парсер Networkly.app — события хакатоны.рус (замена прямого парсинга hackathons.ru).

Networkly.app — платформа IT-событий, community/hackathon — данные от хакатоны.рус.
Статический HTML, без JavaScript — httpx + selectolax достаточно.
"""

from __future__ import annotations

import hashlib
import re

import httpx
from selectolax.parser import HTMLParser

from app.parsers.base import BaseParser, RawHackathon

BASE_URL = "https://networkly.app"


class NetworklyParser(BaseParser):
    """Парсер событий хакатоны.рус через Networkly.app."""

    source_name = "hackathons_ru"

    # Страницы с хакатонами
    URLS = [
        "https://networkly.app/community/hackathon",
        "https://networkly.app/event?event_filter[tags][]=хакатон",
        "https://networkly.app/event?event_filter[tags][]=hackathon",
    ]

    async def fetch_all(self) -> list[RawHackathon]:
        results: list[RawHackathon] = []
        seen: set[str] = set()

        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30.0,
            headers={"User-Agent": "ComIT-HackathonParser/1.0"},
        ) as client:
            for url in self.URLS:
                try:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    tree = HTMLParser(resp.text)

                    for link in tree.css("a[href*='/event/']"):
                        href = link.attributes.get("href", "")
                        if not href or "event/new" in href or "event_filter" in href:
                            continue
                        if not href.startswith("http"):
                            href = BASE_URL + href
                        # Только страницы конкретных событий (формат /event/slug_ID)
                        path = href.split("?")[0]
                        if not re.search(r"/event/[^/]+_\d+", path):
                            continue
                        if href in seen:
                            continue
                        seen.add(href)

                        title = (link.text() or "").strip()
                        if not title or len(title) < 3:
                            continue
                        skip = [
                            "create event",
                            "it events",
                            "фильтр",
                            "save",
                            "language",
                            "city",
                            "date",
                            "tags",
                        ]
                        if any(s in title.lower() for s in skip):
                            continue

                        # Дата из URL: event/slug-DD-MM-YYYY_ID
                        date_str = self._extract_date_from_url(href)
                        if not date_str:
                            parent = link.parent
                            date_str = self._extract_date(
                                parent.text(separator=" ", strip=True) if parent else ""
                            )

                        external_id = hashlib.sha256(href.encode()).hexdigest()[:32]
                        results.append(
                            RawHackathon(
                                external_id=external_id,
                                source=self.source_name,
                                title=title[:500],
                                start_date=date_str,
                                url=href,
                                is_online=self._is_online(title, href),
                                status="upcoming",
                            )
                        )
                except Exception:
                    continue

        return results[:80]

    def _extract_date_from_url(self, url: str) -> str | None:
        """Извлечь дату из URL вида /event/name-27-02-2025_4708."""
        m = re.search(r"(\d{1,2})-(\d{1,2})-(\d{4})_", url)
        if m:
            day, month, year = m.groups()
            months = [
                "января", "февраля", "марта", "апреля", "мая", "июня",
                "июля", "августа", "сентября", "октября", "ноября", "декабря",
            ]
            if 1 <= int(month) <= 12:
                return f"{day} {months[int(month) - 1]} {year}"
        return None

    def _extract_date(self, text: str) -> str | None:
        m = re.search(
            r"(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|"
            r"августа|сентября|октября|ноября|декабря)\s+(\d{4})",
            text,
            re.I,
        )
        if m:
            return f"{m.group(1)} {m.group(2)} {m.group(3)}"
        return None

    def _is_online(self, title: str, url: str) -> bool:
        return "онлайн" in title.lower() or "online" in title.lower()

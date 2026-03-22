"""Парсер cups.online (All Cups) — соревнования и хакатоны."""

from __future__ import annotations

import hashlib
import re

import httpx
from selectolax.parser import HTMLParser

from app.parsers.base import BaseParser, RawHackathon


class CupsOnlineParser(BaseParser):
    source_name = "cups_online"

    BASE_URL = "https://cups.online"
    CONTESTS_URL = "https://cups.online/ru/contests/"

    async def fetch_all(self) -> list[RawHackathon]:
        results: list[RawHackathon] = []
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30.0,
            headers={"User-Agent": "ComIT-HackathonParser/1.0"},
        ) as client:
            resp = await client.get(self.CONTESTS_URL)
            resp.raise_for_status()
            tree = HTMLParser(resp.text)

        seen: set[str] = set()
        for link in tree.css("a[href*='/contests/'], a[href*='/rounds/']"):
            href = link.attributes.get("href", "")
            if not href or "contests" not in href:
                continue
            if not href.startswith("http"):
                href = self.BASE_URL + href
            if href in seen:
                continue
            seen.add(href)

            title = (link.text() or "").strip()
            if not title or len(title) < 2:
                continue

            # Пропускаем слишком общие/технические
            skip = ["задачи", "домашнее задание", "round", "раунд"]
            if any(s in title.lower() for s in skip) and len(title) < 20:
                continue

            parent = link.parent
            sibling_text = ""
            if parent:
                sibling_text = parent.text(separator=" ", strip=True)
            date_str = self._extract_date(sibling_text)
            external_id = hashlib.sha256(href.encode()).hexdigest()[:32]

            results.append(
                RawHackathon(
                    external_id=external_id,
                    source=self.source_name,
                    title=title,
                    description=None,
                    start_date=date_str,
                    url=href,
                    is_online=True,
                    status="upcoming",
                )
            )

        return results[:100]  # Ограничение для cups — много соревнований

    def _extract_date(self, text: str) -> str | None:
        m = re.search(
            r"(\d{1,2})\s*(?:[-–]\s*)?(\d{1,2})?\s*(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s*(?:[-–]\s*)?(\d{1,2})?\s*(\d{4})?",
            text,
            re.I,
        )
        if m:
            parts = [p for p in m.groups() if p]
            return " ".join(parts) if parts else None
        m2 = re.search(r"(\d{1,2})\s+(\d{1,2})\s+(\d{4})", text)
        if m2:
            return f"{m2.group(1)} {m2.group(2)} {m2.group(3)}"
        return None

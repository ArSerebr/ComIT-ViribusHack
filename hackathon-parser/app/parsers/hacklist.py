"""Парсер hacklist.ru — календарь хакатонов."""

from __future__ import annotations

import hashlib
import re

import httpx
from selectolax.parser import HTMLParser

from app.parsers.base import BaseParser, RawHackathon


class HacklistParser(BaseParser):
    source_name = "hacklist"

    BASE_URL = "https://hacklist.ru"

    async def fetch_all(self) -> list[RawHackathon]:
        results: list[RawHackathon] = []
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30.0,
            headers={"User-Agent": "ComIT-HackathonParser/1.0"},
        ) as client:
            resp = await client.get(self.BASE_URL)
            resp.raise_for_status()
            tree = HTMLParser(resp.text)

        # Ищем все h3 с ссылками на хакатоны (основная структура hacklist)
        for link in tree.css("h3 a[href*='/itevents/'], h3 a[href*='/hackathons/']"):
            href = link.attributes.get("href", "")
            if not href or "/hackathons/hackathons" in href:
                continue
            if not href.startswith("http"):
                href = self.BASE_URL + href
            title = (link.text() or "").strip()
            if not title or len(title) < 3:
                continue
            # Контейнер — родитель h3 или выше
            card = link.parent
            while card and card.tag != "body":
                if card.parent:
                    card = card.parent
                    break
                card = card.parent
            raw = self._parse_card(card or link.parent, link, href, title)
            if raw:
                results.append(raw)

        # Fallback: ищем все ссылки на хакатоны
        if not results:
            for link in tree.css("a[href*='/itevents/'], a[href*='/hackathons/']"):
                href = link.attributes.get("href", "")
                if not href or href == "/hackathons/hackathons/":
                    continue
                if not href.startswith("http"):
                    href = self.BASE_URL + href
                raw = self._parse_from_link(link, href)
                if raw:
                    results.append(raw)

        # Дедупликация по url
        seen: set[str] = set()
        unique: list[RawHackathon] = []
        for r in results:
            key = r.url or r.external_id
            if key and key not in seen:
                seen.add(key)
                unique.append(r)
        return unique

    def _parse_card(self, node, link=None, href=None, title=None) -> RawHackathon | None:
        if link is None or href is None or title is None:
            link = node.css_first("a[href*='/itevents/'], a[href*='/hackathons/']")
            if not link:
                return None
            href = link.attributes.get("href", "")
            if not href or "/hackathons/hackathons" in href:
                return None
            if not href.startswith("http"):
                href = self.BASE_URL + href
            title = (link.text() or "").strip()
            if not title or len(title) < 3:
                return None

        # Дата, призы, локация — из текста карточки
        date_str = None
        prize = None
        location = None
        is_online = False

        full_text = node.text(separator=" ", strip=True)
        date_str = self._extract_date(full_text)

        if "руб" in full_text.lower() or "₽" in full_text:
            prize = self._extract_prize(full_text)
        if "онлайн" in full_text.lower():
            is_online = True
        if "офлайн" in full_text.lower() or "москва" in full_text.lower() or "казань" in full_text.lower():
            loc_match = re.search(
                r"(Офлайн|Онлайн)[,\s]*(?:Офлайн)?[,\s]*([А-Яа-яёЁ\s\-]+)?|(Москва|Казань|Пермь|Санкт-Петербург)",
                full_text,
            )
            if loc_match:
                location = (loc_match.group(2) or loc_match.group(3) or "").strip() or "Офлайн"

        tags = []
        for tag_link in node.css("a[href*='/tags/'], a[href*='/events/tags/']"):
            t = (tag_link.text() or "").strip()
            if t and t not in tags:
                tags.append(t)

        external_id = hashlib.sha256(href.encode()).hexdigest()[:32]

        # Статус по секции — если карточка в "прошедшие"
        status = "upcoming"

        return RawHackathon(
            external_id=external_id,
            source=self.source_name,
            title=title,
            description=None,
            start_date=date_str,
            end_date=None,
            location=location or ("Онлайн" if is_online else None),
            is_online=is_online,
            prize_pool=prize,
            url=href,
            image_url=None,
            tags=tags if tags else None,
            status=status,
        )

    def _parse_from_link(self, link, href: str) -> RawHackathon | None:
        title = (link.text() or "").strip()
        if not title or len(title) < 3:
            return None
        parent = link.parent
        full_text = parent.text(separator=" ", strip=True) if parent else ""
        date_str = self._extract_date(full_text)
        prize = self._extract_prize(full_text) if "руб" in full_text.lower() or "₽" in full_text else None
        is_online = "онлайн" in full_text.lower()
        external_id = hashlib.sha256(href.encode()).hexdigest()[:32]
        return RawHackathon(
            external_id=external_id,
            source=self.source_name,
            title=title,
            start_date=date_str,
            is_online=is_online,
            prize_pool=prize,
            url=href,
            status="upcoming",
        )

    def _extract_date(self, text: str) -> str | None:
        m = re.search(
            r"(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(\d{4})",
            text,
            re.I,
        )
        if m:
            return f"{m.group(1)} {m.group(2)} {m.group(3)}"
        return None

    def _extract_prize(self, text: str) -> str | None:
        m = re.search(r"([\d\s]+)\s*(?:руб|₽)", text)
        if m:
            return (m.group(1) or "").strip() + " рублей"
        return None

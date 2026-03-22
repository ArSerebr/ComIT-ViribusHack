"""Определение, относится ли хакатон к ещё не завершившимся (предстоящим / идущим)."""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone

from app.modules.hackathons.models import Hackathon

# Как в hacklist / networkly / cups (hackathon-parser): «22 марта 2026»
_RU_MONTHS = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}

_RE_RU_DATE = re.compile(
    r"(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|"
    r"сентября|октября|ноября|декабря)\s+(\d{4})",
    re.IGNORECASE,
)

_RE_DMY_SEP = re.compile(r"^(\d{1,2})[./-](\d{1,2})[./-](\d{4})\s*$")

_RE_SPACED_DMY = re.compile(r"^(\d{1,2})\s+(\d{1,2})\s+(\d{4})\s*$")


def _parse_russian_or_numeric_date(raw: str) -> date | None:
    """Даты из парсера: «15 марта 2026», также DD.MM.YYYY и «D M YYYY» (день месяц год)."""
    m = _RE_RU_DATE.search(raw)
    if m:
        d, mon, y = int(m.group(1)), m.group(2).lower(), int(m.group(3))
        month = _RU_MONTHS.get(mon)
        if month:
            try:
                return date(y, month, d)
            except ValueError:
                return None

    m2 = _RE_DMY_SEP.match(raw.strip())
    if m2:
        d, month, y = int(m2.group(1)), int(m2.group(2)), int(m2.group(3))
        try:
            return date(y, month, d)
        except ValueError:
            return None

    m3 = _RE_SPACED_DMY.match(raw.strip())
    if m3:
        d, month, y = int(m3.group(1)), int(m3.group(2)), int(m3.group(3))
        try:
            return date(y, month, d)
        except ValueError:
            return None

    return None


def _parse_start(s: str | None) -> tuple[datetime | None, date | None]:
    """Возвращает (момент старта UTC, либо только календарную дату)."""
    if not s or not str(s).strip():
        return None, None
    raw = str(s).strip()
    try:
        if "T" in raw or raw.endswith("Z") or (len(raw) > 10 and raw[10] in "+-"):
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc), None
        if len(raw) >= 10 and raw[4] == "-" and raw[7] == "-":
            d = date.fromisoformat(raw[:10])
            return None, d
    except ValueError:
        pass

    rd = _parse_russian_or_numeric_date(raw)
    if rd is not None:
        return None, rd

    return None, None


def _parse_end(s: str | None) -> tuple[datetime | None, date | None]:
    return _parse_start(s)


def hackathon_is_upcoming(h: Hackathon, *, now: datetime | None = None) -> bool:
    """
    True, если событие ещё не закончилось: конец в будущем или (без конца) старт не раньше сегодняшнего дня UTC.

    Для даты без времени считаем день целиком: старт «2026-04-01» виден до конца этого дня UTC.
    """
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    now = now.astimezone(timezone.utc)

    end_dt, end_d = _parse_end(h.end_date)
    start_dt, start_d = _parse_start(h.start_date)

    if end_dt is not None:
        return end_dt > now
    if end_d is not None:
        end_day_end = datetime.combine(
            end_d + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc
        )
        return end_day_end > now

    if start_dt is not None:
        return start_dt > now
    if start_d is not None:
        start_day_end = datetime.combine(
            start_d + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc
        )
        return start_day_end > now

    return False

"""Данные новости до сохранения в БД."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class RawItNews:
    external_id: str
    source: str
    title: str
    summary: str | None
    url: str
    published_at: datetime | None

"""Базовый класс парсера."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RawHackathon:
    """Нормализованные данные хакатона для сохранения в БД."""

    external_id: str
    source: str
    title: str
    description: str | None = None
    description_raw: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    registration_deadline: str | None = None
    location: str | None = None
    is_online: bool = False
    prize_pool: str | None = None
    url: str | None = None
    image_url: str | None = None
    organizer: str | None = None
    tags: list[str] | None = None
    status: str = "upcoming"


class BaseParser(ABC):
    source_name: str = ""

    @abstractmethod
    async def fetch_all(self) -> list[RawHackathon]:
        """Получить список хакатонов с источника."""
        ...

"""Ключ дедупликации для хакатонов."""

from __future__ import annotations

import hashlib
import re


def compute_dedup_key(title: str, start_date: str | None) -> str:
    """Вычисляет ключ для объединения дубликатов из разных источников."""
    normalized_title = re.sub(r"\s+", " ", title.lower().strip())
    normalized_title = re.sub(r"[^\w\s]", "", normalized_title, flags=re.UNICODE)
    date_part = (start_date or "").strip()
    raw = f"{normalized_title}|{date_part}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()

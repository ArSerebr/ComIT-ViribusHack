"""ASCII slugs for URL paths: Cyrillic → Latin, then [a-z0-9-]."""

from __future__ import annotations

import re

# Russian + common Cyrillic letters (GOST-like / practical Latin)
_CYR_TO_LAT: dict[str, str] = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "e",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "h",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "sch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
    "і": "i",
    "ї": "yi",
    "є": "ye",
    "ґ": "g",
    "ў": "u",
    "җ": "zh",
    "қ": "k",
    "ң": "n",
    "ү": "u",
    "ұ": "u",
    "һ": "h",
    "ә": "a",
    "ө": "o",
}


def transliterate_cyrillic_to_latin(text: str) -> str:
    """Replace known Cyrillic characters with Latin; leave other chars as-is."""
    out: list[str] = []
    for ch in text:
        mapped = _CYR_TO_LAT.get(ch.lower())
        if mapped is not None:
            out.append(mapped)
        else:
            out.append(ch)
    return "".join(out)


def slugify_project_identifier(
    raw_id: str,
    *,
    title: str | None = None,
    max_len: int = 240,
) -> str:
    """
    Build a URL-safe ASCII slug from client ``id`` (and optionally ``title`` fallback).

    Strips to ``[a-z0-9-]``; empty result becomes ``project``.
    """
    raw = (raw_id or "").strip()
    if not raw:
        raw = (title or "").strip()
    if not raw:
        raw = "project"
    t = transliterate_cyrillic_to_latin(raw)
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", "-", t)
    t = re.sub(r"-+", "-", t).strip("-")
    if not t:
        t = "project"
    return t[:max_len]


def project_details_path(project_id: str) -> str:
    """Relative URL for project details (matches frontend ``/projects/:id``)."""
    return f"/projects/{project_id}"

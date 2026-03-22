"""Загрузка recommendation_catalog из CSV и строк hackathon (вызывается из seed_db)."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.hackathons.models import Hackathon
from app.modules.hackathons.upcoming import hackathon_is_upcoming
from app.modules.recommendations.models import RecommendationCatalogItem

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "recommendation_catalog"

DEFAULT_IMG_PROJECT = "/img/poster-120-1.jpg"
DEFAULT_IMG_COURSE = "/img/course-image.png"
DEFAULT_IMG_ARTICLE = "/img/news-photo.jpg"
DEFAULT_IMG_HACK = "/img/poster-hackathon.jpg"


def _slug_topics(*parts: str) -> str:
    raw = " | ".join(p for p in parts if p and str(p).strip())
    if not raw:
        return "general"
    topics = []
    for seg in re.split(r"\s*\|\s*", raw):
        t = seg.strip().lower().replace(" ", "_").replace("/", "_")
        if t:
            topics.append(t)
    return "|".join(topics) if topics else "general"


def _norm_skills(cell: str) -> str:
    if not cell or not str(cell).strip():
        return ""
    parts = []
    for seg in re.split(r"\s*\|\s*", cell):
        s = seg.strip().lower().replace(" ", "_").replace("/", "_")
        if s:
            parts.append(s)
    return "|".join(parts)


def _stable_id(prefix: str, raw_id: str) -> str:
    s = raw_id.strip().lstrip("#").replace(" ", "_")
    return f"{prefix}_{s}"


def _read_projects(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            pid = row.get("project_id", "").strip()
            if not pid:
                continue
            title = (row.get("title") or "").strip()
            short = (row.get("short_description") or title)[:500]
            sphere = (row.get("sphere") or "").strip()
            primary = (row.get("primary_skill") or "").strip()
            subtitle = short if len(short) < 400 else short[:397] + "..."
            topics = _slug_topics(sphere, primary)
            skills = _norm_skills(row.get("required_skills", ""))
            rows.append({
                "id": _stable_id("proj", pid),
                "kind": "project",
                "title": title or pid,
                "subtitle": subtitle,
                "image_url": DEFAULT_IMG_PROJECT,
                "link_url": "/#/projects",
                "topics": topics,
                "skills": skills,
                "sort_order": i,
            })
    return rows


def _read_courses(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            cid = row.get("course_id", "").strip()
            if not cid:
                continue
            title = (row.get("title") or "").strip()
            short = (row.get("short_description") or title)[:500]
            sphere = (row.get("sphere") or "").strip()
            primary = (row.get("primary_skill") or "").strip()
            dh = row.get("duration_hours", "").strip()
            extra = f"{dh} ч" if dh else ""
            subtitle = short
            if extra:
                subtitle = f"{subtitle} · {extra}" if subtitle else extra
            topics = _slug_topics(sphere, primary)
            skills = _norm_skills(row.get("related_skills", ""))
            rows.append({
                "id": _stable_id("course", cid),
                "kind": "course",
                "title": title or cid,
                "subtitle": subtitle[:500],
                "image_url": DEFAULT_IMG_COURSE,
                "link_url": "/#/library",
                "topics": topics,
                "skills": skills,
                "sort_order": 10_000 + i,
            })
    return rows


def _read_articles(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            aid = row.get("article_id", "").strip()
            if not aid:
                continue
            title = (row.get("title") or "").strip()
            summary = (row.get("summary") or title)[:500]
            sphere = (row.get("sphere") or "").strip()
            primary = (row.get("primary_skill") or "").strip()
            minutes = row.get("estimated_read_minutes", "").strip()
            subtitle = summary
            if minutes:
                subtitle = f"{subtitle} · {minutes} мин" if subtitle else f"{minutes} мин"
            topics = _slug_topics(sphere, primary)
            skills = _norm_skills(row.get("related_skills", ""))
            rows.append({
                "id": _stable_id("article", aid),
                "kind": "article",
                "title": title or aid,
                "subtitle": subtitle[:500],
                "image_url": DEFAULT_IMG_ARTICLE,
                "link_url": "/#/library",
                "topics": topics,
                "skills": skills,
                "sort_order": 20_000 + i,
            })
    return rows


async def _hackathon_rows(session: AsyncSession) -> list[dict[str, Any]]:
    result = await session.execute(select(Hackathon).order_by(Hackathon.start_date.asc().nullslast()))
    all_h = list(result.scalars().all())
    upcoming = [h for h in all_h if hackathon_is_upcoming(h)]
    rows: list[dict[str, Any]] = []
    for i, h in enumerate(upcoming):
        hid = f"hack_{h.id}"
        loc = (h.location or "").strip()
        dates = " — ".join(x for x in (h.start_date, h.end_date) if x)
        subtitle = " · ".join(x for x in (dates, loc) if x) or (h.description or "")[:200]
        link = (h.url or "").strip() or "/#/news"
        img = (h.image_url or "").strip() or DEFAULT_IMG_HACK
        tags = h.tags if isinstance(h.tags, list) else []
        topics = _slug_topics(*[str(t) for t in tags[:5]]) if tags else "hackathon"
        rows.append({
            "id": hid,
            "kind": "hackathon",
            "title": h.title,
            "subtitle": subtitle[:500],
            "image_url": img[:2048],
            "link_url": link[:2048],
            "topics": topics,
            "skills": "",
            "sort_order": 30_000 + i,
        })
    return rows


async def run_recommendation_catalog_seed(session: AsyncSession, wipe: bool) -> None:
    if wipe:
        await session.execute(text("TRUNCATE recommendation_catalog"))

    batch: list[dict[str, Any]] = []
    batch.extend(_read_projects(DATA_DIR / "projects.csv"))
    batch.extend(_read_courses(DATA_DIR / "courses.csv"))
    batch.extend(_read_articles(DATA_DIR / "articles.csv"))
    batch.extend(await _hackathon_rows(session))

    for row in batch:
        await session.merge(
            RecommendationCatalogItem(
                id=row["id"],
                kind=row["kind"],
                title=row["title"],
                subtitle=row["subtitle"],
                image_url=row["image_url"],
                link_url=row["link_url"],
                topics=row.get("topics"),
                skills=row.get("skills") or None,
                is_active=True,
                sort_order=row["sort_order"],
            )
        )

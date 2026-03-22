#!/usr/bin/env python3
"""
Одноразовый конвертер: массив карточек рекомендаций (как в ответе API) → CSV.

Пример (из корня репозитория):
  python scripts/json_recommendations_to_csv.py \\
    --input response_1774186282905.json \\
    --output-dir backend/data/recommendation_catalog

По умолчанию пишет один файл recommendation_catalog_export.csv (id, kind, поля как в БД).

Флаг --split дополнительно создаёт projects/courses/articles CSV с заголовками как у seed
(можно вручную слить с существующими файлами) и other_cards.csv для hack_* и прочих id.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


def _infer_kind(card_id: str) -> str:
    cid = (card_id or "").strip()
    if cid.startswith("proj_"):
        return "project"
    if cid.startswith("course_"):
        return "course"
    if cid.startswith("article_"):
        return "article"
    if cid.startswith("hack_"):
        return "hackathon"
    return "promo"


def _strip_prefix_id(card_id: str, prefix: str) -> str:
    raw = (card_id or "").strip()
    if raw.startswith(prefix):
        raw = raw[len(prefix) :]
    if not raw.startswith("#"):
        raw = f"#{raw}"
    return raw


def _parse_read_minutes(subtitle: str) -> str:
    m = re.search(r"·\s*(\d+)\s*мин", subtitle or "")
    return m.group(1) if m else ""


PROJECTS_FIELDNAMES = [
    "project_id",
    "visibility",
    "sphere",
    "project_format",
    "title",
    "short_description",
    "full_description",
    "captain_name",
    "captain_primary_skill",
    "primary_skill",
    "required_skills",
    "current_team_size",
    "team_size_needed",
    "project_stage",
    "timeline_weeks",
    "last_activity_days_ago",
]

COURSES_FIELDNAMES = [
    "course_id",
    "visibility",
    "sphere",
    "course_format",
    "title",
    "short_description",
    "learning_outcomes",
    "difficulty_level",
    "duration_hours",
    "modules_count",
    "lessons_count",
    "practice_format",
    "mentor_name",
    "primary_skill",
    "related_skills",
    "course_status",
    "certificate",
    "last_activity_days_ago",
]

ARTICLES_FIELDNAMES = [
    "article_id",
    "visibility",
    "sphere",
    "article_format",
    "title",
    "summary",
    "target_audience",
    "difficulty_level",
    "estimated_read_minutes",
    "primary_skill",
    "related_skills",
    "author_name",
    "article_status",
    "tags",
    "last_activity_days_ago",
]

UNIFIED_FIELDNAMES = [
    "id",
    "kind",
    "title",
    "subtitle",
    "image_url",
    "link_url",
    "topics",
    "skills",
    "sort_order",
]


def _project_row(item: dict) -> dict[str, str]:
    title = (item.get("title") or "").strip()
    subtitle = (item.get("subtitle") or title).strip()
    pid = _strip_prefix_id(item.get("id", ""), "proj_")
    return {
        "project_id": pid,
        "visibility": "Публичный",
        "sphere": "General",
        "project_format": "product",
        "title": title,
        "short_description": subtitle[:500],
        "full_description": subtitle,
        "captain_name": "",
        "captain_primary_skill": "",
        "primary_skill": "",
        "required_skills": "",
        "current_team_size": "",
        "team_size_needed": "",
        "project_stage": "idea",
        "timeline_weeks": "",
        "last_activity_days_ago": "",
    }


def _course_row(item: dict) -> dict[str, str]:
    title = (item.get("title") or "").strip()
    subtitle = (item.get("subtitle") or title).strip()
    cid = _strip_prefix_id(item.get("id", ""), "course_")
    return {
        "course_id": cid,
        "visibility": "Публичный",
        "sphere": "General",
        "course_format": "course",
        "title": title,
        "short_description": subtitle[:500],
        "learning_outcomes": "",
        "difficulty_level": "intermediate",
        "duration_hours": "",
        "modules_count": "",
        "lessons_count": "",
        "practice_format": "",
        "mentor_name": "",
        "primary_skill": "",
        "related_skills": "",
        "course_status": "published",
        "certificate": "",
        "last_activity_days_ago": "",
    }


def _article_row(item: dict) -> dict[str, str]:
    title = (item.get("title") or "").strip()
    subtitle = (item.get("subtitle") or title).strip()
    aid = _strip_prefix_id(item.get("id", ""), "article_")
    minutes = _parse_read_minutes(subtitle)
    summary = re.sub(r"\s*·\s*\d+\s*мин\s*$", "", subtitle).strip() or title
    return {
        "article_id": aid,
        "visibility": "Публичный",
        "sphere": "General",
        "article_format": "article",
        "title": title,
        "summary": summary[:500],
        "target_audience": "",
        "difficulty_level": "intermediate",
        "estimated_read_minutes": minutes,
        "primary_skill": "",
        "related_skills": "",
        "author_name": "",
        "article_status": "published",
        "tags": "",
        "last_activity_days_ago": "",
    }


def load_cards(path: Path) -> list[dict]:
    raw = path.read_text(encoding="utf-8-sig")
    data = json.loads(raw)
    if not isinstance(data, list):
        raise SystemExit(f"Ожидался JSON-массив, получено: {type(data).__name__}")
    return [x for x in data if isinstance(x, dict)]


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--input",
        "-i",
        type=Path,
        default=Path("response_1774186282905.json"),
        help="JSON с массивом объектов {id,title,subtitle,image,link}",
    )
    p.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=Path("."),
        help="Каталог для CSV",
    )
    p.add_argument(
        "--split",
        action="store_true",
        help="Дополнительно записать projects/courses/articles/other_cards CSV для seed",
    )
    args = p.parse_args()

    if not args.input.is_file():
        raise SystemExit(f"Файл не найден: {args.input.resolve()}")

    cards = load_cards(args.input)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    unified_path = args.output_dir / "recommendation_catalog_export.csv"
    with unified_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=UNIFIED_FIELDNAMES, extrasaction="ignore")
        w.writeheader()
        for i, item in enumerate(cards):
            cid = (item.get("id") or "").strip()
            kind = _infer_kind(cid)
            w.writerow(
                {
                    "id": cid,
                    "kind": kind,
                    "title": (item.get("title") or "").strip(),
                    "subtitle": (item.get("subtitle") or "").strip(),
                    "image_url": (item.get("image") or "").strip(),
                    "link_url": (item.get("link") or "").strip(),
                    "topics": "",
                    "skills": "",
                    "sort_order": str(i),
                }
            )

    print(f"Записано: {unified_path.resolve()} ({len(cards)} строк)")

    if not args.split:
        return

    projects: list[dict[str, str]] = []
    courses: list[dict[str, str]] = []
    articles: list[dict[str, str]] = []
    other: list[dict[str, str]] = []

    for i, item in enumerate(cards):
        cid = (item.get("id") or "").strip()
        if cid.startswith("proj_"):
            projects.append(_project_row(item))
        elif cid.startswith("course_"):
            courses.append(_course_row(item))
        elif cid.startswith("article_"):
            articles.append(_article_row(item))
        else:
            other.append(
                {
                    "id": cid,
                    "kind": _infer_kind(cid),
                    "title": (item.get("title") or "").strip(),
                    "subtitle": (item.get("subtitle") or "").strip(),
                    "image_url": (item.get("image") or "").strip(),
                    "link_url": (item.get("link") or "").strip(),
                    "sort_order": str(i),
                }
            )

    split_files: list[tuple[str, list[dict[str, str]], list[str]]] = [
        ("projects_from_json.csv", projects, PROJECTS_FIELDNAMES),
        ("courses_from_json.csv", courses, COURSES_FIELDNAMES),
        ("articles_from_json.csv", articles, ARTICLES_FIELDNAMES),
    ]
    for name, rows, fields in split_files:
        out = args.output_dir / name
        with out.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        print(f"Записано: {out.resolve()} ({len(rows)} строк)")

    other_path = args.output_dir / "other_cards_from_json.csv"
    other_fields = ["id", "kind", "title", "subtitle", "image_url", "link_url", "sort_order"]
    with other_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=other_fields)
        w.writeheader()
        w.writerows(other)
    print(f"Записано: {other_path.resolve()} ({len(other)} строк)")


if __name__ == "__main__":
    main()

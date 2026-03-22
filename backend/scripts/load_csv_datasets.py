"""Импорт статей, курсов и проектов из CSV в PostgreSQL.

Перед запуском выполните миграции: ``alembic upgrade head`` (нужна таблица ``library_course``).

Пример::

  cd backend
  python -m scripts.load_csv_datasets \\
    --articles C:/Users/you/Downloads/articles_dataset.csv \\
    --courses C:/Users/you/Downloads/courses_dataset.csv \\
    --projects C:/Users/you/Downloads/projects_dataset.csv

По умолчанию ищет файлы в ``~/Downloads/`` (``articles_dataset.csv`` и т.д.).

Переменные окружения: как у приложения (``DATABASE_URL`` / настройки из ``app.config``).
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings
from app.modules.library.models import LibraryArticle, LibraryArticleTag, LibraryCourse, LibraryTag
from app.modules.projects.models import ProjectsColumn, ProjectsProject, ProjectsProjectDetail
from sqlalchemy import delete, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DEFAULT_AVATAR = "/img/avatar-photo.jpg"

TAG_TONES = ("green", "cyan", "coral", "yellow", "violet")

PROJECT_HUB_COLUMNS: tuple[tuple[str, str, int], ...] = (
    ("idea", "На стадии идеи", 0),
    ("development", "В разработке", 1),
    ("integrated", "Интегрированные", 2),
)

STAGE_TO_COLUMN: dict[str, str] = {
    "idea": "idea",
    "mvp": "development",
    "prototype": "development",
    "beta": "development",
    "growth": "development",
}


def _downloads_default(name: str) -> Path:
    return Path.home() / "Downloads" / name


def _norm_public_id(raw: str) -> str:
    return raw.strip().removeprefix("#").lower()


def _visibility_ru(value: str) -> str | None:
    v = value.strip().lower()
    if "публичн" in v:
        return "public"
    if "приватн" in v:
        return "private"
    return None


def _split_pipe(value: str) -> list[str]:
    return [p.strip() for p in value.split("|") if p.strip()]


def _tag_id(label: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", label.lower().strip())
    base = base.strip("-") or "tag"
    return base[:64]


def _int_or_none(value: str) -> int | None:
    s = value.strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def _bool_certificate(value: str) -> bool | None:
    s = value.strip().lower()
    if s in ("yes", "да", "true", "1"):
        return True
    if s in ("no", "нет", "false", "0"):
        return False
    return None


def _days_ago_label(value: str) -> str:
    n = _int_or_none(value)
    if n is None:
        return "недавно"
    if n == 0:
        return "сегодня"
    if n == 1:
        return "1 день назад"
    if 2 <= n <= 4:
        return f"{n} дня назад"
    return f"{n} дней назад"


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _default_detail_blocks(
    captain_name: str,
    short_description: str,
    full_description: str,
) -> dict:
    preview_name = captain_name.strip() or "Капитан команды"
    blocks: dict = {
        "teamMembersPreview": [
            {
                "id": "captain-preview",
                "name": preview_name,
                "avatarUrl": DEFAULT_AVATAR,
                "avatarVariant": "default",
            }
        ],
        "productivity": {"value": "—", "delta": "—"},
        "progress": {"value": "0%", "percent": 0},
        "todo": {
            "task": (short_description.strip() or "Описание проекта")[:500],
            "updatedLabel": "импорт",
        },
        "integrations": [],
        "participants": [],
    }
    synopsis = full_description.strip()
    if synopsis:
        blocks["importSynopsis"] = synopsis
    return blocks


async def ensure_project_columns(session: AsyncSession) -> None:
    for col_id, title, sort_order in PROJECT_HUB_COLUMNS:
        row = ProjectsColumn(id=col_id, title=title, sort_order=sort_order)
        await session.merge(row)


async def load_articles(session: AsyncSession, path: Path) -> int:
    rows = _read_csv_rows(path)
    tag_by_id: dict[str, LibraryTag] = {}
    for row in rows:
        for label in _split_pipe(row.get("tags", "")):
            tid = _tag_id(label)
            if tid in tag_by_id:
                continue
            tone = TAG_TONES[len(tag_by_id) % len(TAG_TONES)]
            display = label if label.startswith("#") else f"#{label}"
            tag_by_id[tid] = LibraryTag(
                id=tid,
                label=display[:255],
                tone=tone,
                sort_order=None,
            )
    for t in tag_by_id.values():
        await session.merge(t)
    await session.flush()

    n = 0
    for row in rows:
        aid = _norm_public_id(row.get("article_id", ""))
        if not aid:
            continue
        title = row.get("title", "").strip()
        if not title:
            continue
        summary = row.get("summary", "").strip()
        author = row.get("author_name", "").strip() or "Автор"
        tag_labels = _split_pipe(row.get("tags", ""))
        article = LibraryArticle(
            id=aid,
            title=title,
            description=summary or title,
            author_name=author,
            author_avatar_url=DEFAULT_AVATAR,
            owner_user_id=None,
        )
        await session.merge(article)
        await session.execute(delete(LibraryArticleTag).where(LibraryArticleTag.article_id == aid))
        for pos, label in enumerate(tag_labels):
            tid = _tag_id(label)
            link = LibraryArticleTag(article_id=aid, tag_id=tid, position=pos)
            await session.merge(link)
        n += 1
    return n


async def load_courses(session: AsyncSession, path: Path) -> int:
    rows = _read_csv_rows(path)
    n = 0
    for row in rows:
        cid = _norm_public_id(row.get("course_id", ""))
        if not cid:
            continue
        code = row.get("course_id", "").strip()
        if not code.startswith("#"):
            code = f"#{code.upper()}"
        title = row.get("title", "").strip()
        if not title:
            continue
        course = LibraryCourse(
            id=cid,
            code=code[:32],
            visibility=_visibility_ru(row.get("visibility", "")),
            sphere=(row.get("sphere") or "").strip() or None,
            course_format=(row.get("course_format") or "").strip() or None,
            title=title,
            short_description=(row.get("short_description") or "").strip() or title,
            learning_outcomes=(row.get("learning_outcomes") or "").strip() or None,
            difficulty_level=(row.get("difficulty_level") or "").strip() or None,
            duration_hours=_int_or_none(row.get("duration_hours", "")),
            modules_count=_int_or_none(row.get("modules_count", "")),
            lessons_count=_int_or_none(row.get("lessons_count", "")),
            practice_format=(row.get("practice_format") or "").strip() or None,
            mentor_name=(row.get("mentor_name") or "").strip() or None,
            primary_skill=(row.get("primary_skill") or "").strip() or None,
            related_skills=(row.get("related_skills") or "").strip() or None,
            course_status=(row.get("course_status") or "").strip() or None,
            certificate=_bool_certificate(row.get("certificate", "")),
            last_activity_days_ago=_int_or_none(row.get("last_activity_days_ago", "")),
        )
        await session.merge(course)
        n += 1
    return n


async def load_projects(session: AsyncSession, path: Path) -> int:
    await ensure_project_columns(session)
    rows = _read_csv_rows(path)
    n = 0
    sort_by_column: dict[str, int] = {c[0]: 0 for c in PROJECT_HUB_COLUMNS}
    for row in rows:
        raw_id = row.get("project_id", "").strip()
        pid = _norm_public_id(raw_id)
        if not pid:
            continue
        code = raw_id if raw_id.startswith("#") else f"#{raw_id.upper()}"
        title = row.get("title", "").strip()
        if not title:
            continue
        short_d = row.get("short_description", "").strip()
        full_d = row.get("full_description", "").strip()
        captain = row.get("captain_name", "").strip()
        stage = (row.get("project_stage") or "").strip().lower()
        column_id = STAGE_TO_COLUMN.get(stage, "development")
        j = sort_by_column[column_id]
        sort_by_column[column_id] = j + 1

        proj = ProjectsProject(
            id=pid,
            code=code[:32],
            title=title,
            description=short_d or title,
            team_name=captain or "Команда",
            updated_label=_days_ago_label(row.get("last_activity_days_ago", "")),
            team_avatar_url=DEFAULT_AVATAR,
            details_url=f"/projects/{pid}",
            visibility=_visibility_ru(row.get("visibility", "")),
            is_hot=False,
            column_id=column_id,
            sort_order=j,
            owner_user_id=None,
            group_chat_id=None,
        )
        await session.merge(proj)

        blocks = _default_detail_blocks(captain, short_d, full_d)
        detail = ProjectsProjectDetail(
            project_id=pid,
            owner_name=captain or "Капитан",
            join_label="Присоединиться к проекту",
            team_caption="Команда",
            productivity_caption="Прогресс",
            progress_caption="Готовность",
            todo_caption="Задачи",
            integration_caption="Интеграции",
            detail_blocks=blocks,
        )
        await session.merge(detail)
        n += 1
    return n


async def run_load(
    *,
    articles: Path,
    courses: Path,
    projects: Path,
    wipe_library_courses: bool,
    wipe_library_articles: bool,
    wipe_projects: bool,
) -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)
    async with async_session() as session:
        if wipe_library_articles:
            await session.execute(
                text(
                    "TRUNCATE library_article_tag, library_article RESTART IDENTITY CASCADE"
                )
            )
        if wipe_library_courses:
            await session.execute(text('TRUNCATE library_course RESTART IDENTITY CASCADE'))
        if wipe_projects:
            await session.execute(
                text(
                    "TRUNCATE projects_project_detail, projects_project RESTART IDENTITY CASCADE"
                )
            )

        na = await load_articles(session, articles) if articles.exists() else 0
        nc = await load_courses(session, courses) if courses.exists() else 0
        np = await load_projects(session, projects) if projects.exists() else 0

        await session.commit()

    await engine.dispose()
    print(f"Loaded articles: {na}, courses: {nc}, projects: {np}")


def main() -> None:
    p = argparse.ArgumentParser(description="Load articles/courses/projects CSV into DB")
    p.add_argument("--articles", type=Path, default=_downloads_default("articles_dataset.csv"))
    p.add_argument("--courses", type=Path, default=_downloads_default("courses_dataset.csv"))
    p.add_argument("--projects", type=Path, default=_downloads_default("projects_dataset.csv"))
    p.add_argument(
        "--wipe-articles",
        action="store_true",
        help="Truncate library_article (+ tags links) before import",
    )
    p.add_argument(
        "--wipe-courses",
        action="store_true",
        help="Truncate library_course before import",
    )
    p.add_argument(
        "--wipe-projects",
        action="store_true",
        help="Truncate projects_project and details (columns kept)",
    )
    args = p.parse_args()
    missing = [str(x) for x in (args.articles, args.courses, args.projects) if not x.exists()]
    if missing:
        p.error("File not found: " + ", ".join(missing))
    asyncio.run(
        run_load(
            articles=args.articles,
            courses=args.courses,
            projects=args.projects,
            wipe_library_courses=args.wipe_courses,
            wipe_library_articles=args.wipe_articles,
            wipe_projects=args.wipe_projects,
        )
    )


if __name__ == "__main__":
    main()

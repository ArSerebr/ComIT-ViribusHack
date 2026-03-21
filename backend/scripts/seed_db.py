"""Seed database from fixtures. Run after `alembic upgrade head`.

Usage:
  python -m scripts.seed_db                    # all modules, UPSERT (idempotent)
  python -m scripts.seed_db --wipe               # truncate per-module tables then insert (dev)
  python -m scripts.seed_db --module news      # only listed modules (repeatable)
  python -m scripts.seed_db --module projects --wipe
  python -m scripts.seed_db --module auth   # optional admin if SEED_ADMIN_PASSWORD is set

Uses DATABASE_URL from env. Source of truth: PostgreSQL. No in-memory serving.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from collections.abc import Awaitable, Callable, Sequence
from pathlib import Path
from typing import TypeAlias

# Ensure backend is on path when running as module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi_users.password import PasswordHelper
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.modules.auth.models import User
from app.modules.dashboard.models import DashboardHomeSnapshot, DashboardRecommendation
from app.modules.library.models import (
    LibraryArticle,
    LibraryArticleTag,
    LibraryInterestOption,
    LibraryShowcaseItem,
    LibraryTag,
)
from app.modules.news.models import NewsFeatured, NewsMini
from app.modules.notifications.models import NotificationsItem
from app.modules.projects.models import ProjectsColumn, ProjectsProject, ProjectsProjectDetail
from app.seed.fixtures import (
    DASHBOARD_HOME,
    FEATURED_NEWS,
    LIBRARY_BUNDLE,
    NEWS_MINI,
    NOTIFICATIONS,
    PROJECT_DETAILS_BY_ID,
    PROJECT_HUB_COLUMNS,
    RECOMMENDATIONS,
)

SeedFn: TypeAlias = Callable[[AsyncSession, bool], Awaitable[None]]

MODULE_ORDER: tuple[str, ...] = (
    "auth",
    "news",
    "projects",
    "library",
    "notifications",
    "dashboard",
    "analytics",
)


async def seed_auth(session: AsyncSession, wipe: bool) -> None:
    """Optional dev admin: set SEED_ADMIN_PASSWORD (and optionally SEED_ADMIN_EMAIL). Idempotent."""
    if wipe:
        await session.execute(text('TRUNCATE "user" RESTART IDENTITY CASCADE'))
    password = os.environ.get("SEED_ADMIN_PASSWORD", "").strip()
    if not password:
        return
    email = os.environ.get("SEED_ADMIN_EMAIL", "admin@example.com").strip()
    result = await session.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none() is not None:
        return
    ph = PasswordHelper()
    session.add(
        User(
            email=email,
            hashed_password=ph.hash(password),
            is_active=True,
            is_superuser=True,
            is_verified=True,
            role="admin",
        )
    )


async def seed_analytics(session: AsyncSession, wipe: bool) -> None:
    """Analytics tables are event-sourced; seed only clears them on --wipe."""
    if wipe:
        await session.execute(
            text(
                "TRUNCATE analytics_join_request, analytics_interest_event, analytics_like_event "
                "RESTART IDENTITY CASCADE"
            )
        )


async def seed_news(session: AsyncSession, wipe: bool) -> None:
    if wipe:
        await session.execute(text("TRUNCATE news_mini, news_featured RESTART IDENTITY CASCADE"))
    for i, item in enumerate(NEWS_MINI):
        row = NewsMini(
            id=item.id,
            title=item.title,
            image_url=item.imageUrl,
            details_url=item.detailsUrl,
            sort_order=i,
        )
        await session.merge(row)
    for i, item in enumerate(FEATURED_NEWS):
        row = NewsFeatured(
            id=item.id,
            title=item.title,
            subtitle=item.subtitle,
            description=item.description,
            image_url=item.imageUrl,
            cta_label=item.ctaLabel,
            details_url=item.detailsUrl,
            sort_order=i,
        )
        await session.merge(row)


async def seed_projects(session: AsyncSession, wipe: bool) -> None:
    if wipe:
        await session.execute(
            text(
                "TRUNCATE projects_project_detail, projects_project, projects_column RESTART IDENTITY CASCADE"
            )
        )
    for i, col in enumerate(PROJECT_HUB_COLUMNS):
        c_row = ProjectsColumn(id=col.id, title=col.title, sort_order=i)
        await session.merge(c_row)
    for col in PROJECT_HUB_COLUMNS:
        for j, proj in enumerate(col.projects):
            p_row = ProjectsProject(
                id=proj.id,
                code=proj.code,
                title=proj.title,
                description=proj.description,
                team_name=proj.teamName,
                updated_label=proj.updatedLabel,
                team_avatar_url=proj.teamAvatarUrl,
                details_url=proj.detailsUrl,
                visibility=proj.visibility,
                is_hot=proj.isHot,
                column_id=col.id,
                sort_order=j,
            )
            await session.merge(p_row)
    for pid, det in PROJECT_DETAILS_BY_ID.items():
        blocks = {
            "teamMembersPreview": [p.model_dump() for p in det.teamMembersPreview],
            "productivity": det.productivity.model_dump(),
            "progress": det.progress.model_dump(),
            "todo": det.todo.model_dump(),
            "integrations": [i.model_dump() for i in det.integrations],
            "participants": [p.model_dump() for p in det.participants],
        }
        d_row = ProjectsProjectDetail(
            project_id=pid,
            owner_name=det.ownerName,
            join_label=det.joinLabel,
            team_caption=det.teamCaption,
            productivity_caption=det.productivityCaption,
            progress_caption=det.progressCaption,
            todo_caption=det.todoCaption,
            integration_caption=det.integrationCaption,
            detail_blocks=blocks,
        )
        await session.merge(d_row)


async def seed_library(session: AsyncSession, wipe: bool) -> None:
    if wipe:
        await session.execute(
            text(
                "TRUNCATE library_article_tag, library_article, library_showcase_item, "
                "library_interest_option, library_tag RESTART IDENTITY CASCADE"
            )
        )
    for i, s in enumerate(LIBRARY_BUNDLE.showcaseItems):
        row = LibraryShowcaseItem(
            id=s.id,
            brand_label=s.brandLabel,
            eyebrow=s.eyebrow,
            title=s.title,
            image_url=s.imageUrl,
            hero_json=s.hero.model_dump(),
            sort_order=i,
        )
        await session.merge(row)
    for i, opt in enumerate(LIBRARY_BUNDLE.interestOptions):
        row = LibraryInterestOption(
            id=opt.id,
            label=opt.label,
            selected=opt.selected,
            sort_order=i,
        )
        await session.merge(row)
    seen_tags: set[str] = set()
    for art in LIBRARY_BUNDLE.articles:
        for t in art.tags:
            if t.id not in seen_tags:
                seen_tags.add(t.id)
                tg = LibraryTag(id=t.id, label=t.label, tone=t.tone, sort_order=None)
                await session.merge(tg)
    await session.flush()  # теги должны быть в БД до library_article_tag (FK)
    for art in LIBRARY_BUNDLE.articles:
        row = LibraryArticle(
            id=art.id,
            title=art.title,
            description=art.description,
            author_name=art.authorName,
            author_avatar_url=art.authorAvatarUrl,
        )
        await session.merge(row)
        for pos, t in enumerate(art.tags):
            at = LibraryArticleTag(article_id=art.id, tag_id=t.id, position=pos)
            await session.merge(at)


async def seed_notifications(session: AsyncSession, wipe: bool) -> None:
    if wipe:
        await session.execute(text("TRUNCATE notifications_item RESTART IDENTITY CASCADE"))
    for i, n in enumerate(NOTIFICATIONS):
        row = NotificationsItem(
            id=n.id,
            type=n.type,
            title=n.title,
            date_label=n.dateLabel,
            date_caption=n.dateCaption,
            unread=n.unread,
            author_label=n.authorLabel,
            author_name=n.authorName,
            accent_text=n.accentText,
            cta_label=n.ctaLabel,
            path=n.path,
            sort_order=i,
        )
        await session.merge(row)


async def seed_dashboard(session: AsyncSession, wipe: bool) -> None:
    if wipe:
        await session.execute(
            text("TRUNCATE dashboard_recommendation, dashboard_home_snapshot RESTART IDENTITY CASCADE")
        )
    for i, r in enumerate(RECOMMENDATIONS):
        row = DashboardRecommendation(
            id=r.id,
            title=r.title,
            subtitle=r.subtitle,
            image=r.image,
            link=r.link,
            sort_order=i,
        )
        await session.merge(row)
    snap = DashboardHomeSnapshot(id=1, home_json=DASHBOARD_HOME.model_dump())
    await session.merge(snap)


SEED_REGISTRY: dict[str, SeedFn] = {
    "auth": seed_auth,
    "analytics": seed_analytics,
    "news": seed_news,
    "projects": seed_projects,
    "library": seed_library,
    "notifications": seed_notifications,
    "dashboard": seed_dashboard,
}


class SeedOrchestrator:
    """Runs per-module seed functions in dependency-safe order."""

    def __init__(
        self,
        session: AsyncSession,
        *,
        wipe: bool,
        modules: Sequence[str] | None = None,
    ) -> None:
        self._session = session
        self._wipe = wipe
        self._modules = tuple(modules) if modules else MODULE_ORDER

    async def run(self) -> None:
        unknown = [m for m in self._modules if m not in SEED_REGISTRY]
        if unknown:
            raise ValueError(f"Unknown module(s): {', '.join(unknown)}. Valid: {', '.join(MODULE_ORDER)}")
        for name in self._modules:
            await SEED_REGISTRY[name](self._session, self._wipe)


def _parse_modules(raw: list[str] | None) -> tuple[str, ...] | None:
    if not raw:
        return None
    seen: list[str] = []
    for m in raw:
        key = m.strip().lower()
        if key not in seen:
            seen.append(key)
    order_index = {name: i for i, name in enumerate(MODULE_ORDER)}
    return tuple(sorted(seen, key=lambda x: order_index[x]))


async def run_seed(*, wipe: bool, modules: Sequence[str] | None = None) -> None:
    settings = get_settings()
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
    )
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    async with async_session() as session:
        orchestrator = SeedOrchestrator(session, wipe=wipe, modules=modules)
        await orchestrator.run()
        await session.commit()
    await engine.dispose()
    print("Seed completed.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed database from fixtures")
    parser.add_argument("--wipe", action="store_true", help="Truncate tables before seed (dev)")
    parser.add_argument(
        "--module",
        action="append",
        dest="modules",
        metavar="NAME",
        help=f"Seed only this module (repeatable). One of: {', '.join(MODULE_ORDER)}",
    )
    args = parser.parse_args()
    mods = _parse_modules(args.modules)
    if mods:
        unknown = set(mods) - set(MODULE_ORDER)
        if unknown:
            parser.error(f"Unknown module(s): {', '.join(sorted(unknown))}")
    asyncio.run(run_seed(wipe=args.wipe, modules=mods))


if __name__ == "__main__":
    main()

"""Публичный фасад для других модулей: только зависимости, без ORM."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from app.modules.auth.deps import current_active_user, require_roles
from app.modules.auth.models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_emails_by_ids(
    session: AsyncSession, user_ids: Sequence[uuid.UUID]
) -> dict[uuid.UUID, str]:
    """Return user_id -> email for given user IDs."""
    if not user_ids:
        return {}
    stmt = select(User.id, User.email).where(User.id.in_(user_ids))
    rows = (await session.execute(stmt)).all()
    return {r[0]: r[1] for r in rows}


__all__ = ["current_active_user", "require_roles", "get_user_emails_by_ids"]

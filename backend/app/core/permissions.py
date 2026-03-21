"""Shared content-edit rules: owner or moderator/admin."""

from __future__ import annotations

import uuid

from app.modules.auth.models import User


def _user_role(user: User) -> str:
    raw = user.role
    return raw.value if hasattr(raw, "value") else str(raw)


def can_edit_content(user: User, owner_id: uuid.UUID | None) -> bool:
    """True if the user may edit content owned by ``owner_id`` (or system content when ``owner_id`` is None)."""
    role = _user_role(user)
    if role in ("moderator", "admin"):
        return True
    if owner_id is None:
        return False
    return owner_id == user.id


def is_moderator_or_admin(user: User) -> bool:
    return _user_role(user) in ("moderator", "admin")

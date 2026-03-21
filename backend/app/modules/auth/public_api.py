"""Публичный фасад для других модулей: только зависимости, без ORM."""

from __future__ import annotations

from app.modules.auth.deps import current_active_user, require_roles

__all__ = ["current_active_user", "require_roles"]

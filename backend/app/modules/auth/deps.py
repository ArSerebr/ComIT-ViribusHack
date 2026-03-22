"""Зависимости auth: БД пользователей, FastAPI Users, роли."""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

from app.core.db.session import get_db
from app.modules.auth.jwt_backend import auth_backend
from app.modules.auth.manager import UserManager
from app.modules.auth.models import User
from fastapi import Depends, HTTPException
from fastapi_users import FastAPIUsers
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_db(
    session: AsyncSession = Depends(get_db),
) -> AsyncGenerator[SQLAlchemyUserDatabase[User, uuid.UUID], None]:
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase[User, uuid.UUID] = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
current_user_optional = fastapi_users.current_user(active=True, optional=True)


def require_roles(*allowed_roles: str):
    """Зависимость: текущий пользователь с одной из указанных ролей (`user` / `moderator` / `admin`)."""

    allowed = frozenset(allowed_roles)

    async def _require(
        user: User = Depends(current_active_user),
    ) -> User:
        raw = user.role
        role = raw.value if hasattr(raw, "value") else str(raw)
        if role not in allowed:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return _require

"""ORM: пользователь fastapi-users + роль."""
from __future__ import annotations

from enum import StrEnum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import Base
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID


class UserRole(StrEnum):
    user = "user"
    moderator = "moderator"
    admin = "admin"


class User(SQLAlchemyBaseUserTableUUID, Base):
    """Таблица `user`: базовые поля fastapi-users и колонка `role`."""

    role: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="user",
        server_default="user",
    )

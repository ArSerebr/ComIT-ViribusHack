from __future__ import annotations

import uuid
from datetime import datetime

from app.core.db.base import Base
from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column


class AnalyticsLikeEvent(Base):
    __tablename__ = "analytics_like_event"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    entity: Mapped[str] = mapped_column(String(20), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(255), nullable=False)
    ts: Mapped[int] = mapped_column(BigInteger, nullable=False)
    seed_key: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)


class AnalyticsInterestEvent(Base):
    __tablename__ = "analytics_interest_event"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    interests: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    ts: Mapped[int] = mapped_column(BigInteger, nullable=False)


class AnalyticsJoinRequest(Base):
    __tablename__ = "analytics_join_request"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("projects_project.id", ondelete="CASCADE"),
        nullable=False,
    )
    applicant_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

from __future__ import annotations

import uuid

from app.core.db.base import Base
from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class UserProfile(Base):
    __tablename__ = "user_profile"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    )
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)


class UserProfileInterest(Base):
    __tablename__ = "user_profile_interest"
    __table_args__ = (Index("ix_user_profile_interest_interest_id", "interest_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    )
    interest_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("library_interest_option.id", ondelete="RESTRICT"),
        primary_key=True,
    )

from __future__ import annotations

import uuid
from typing import Any

from app.core.db.base import Base
from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column


class LibraryShowcaseItem(Base):
    __tablename__ = "library_showcase_item"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    brand_label: Mapped[str] = mapped_column(String(255), nullable=False)
    eyebrow: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    hero_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )


class LibraryInterestOption(Base):
    __tablename__ = "library_interest_option"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    selected: Mapped[bool] = mapped_column(Boolean, nullable=False)
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )


class LibraryArticle(Base):
    __tablename__ = "library_article"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    author_name: Mapped[str] = mapped_column(String(255), nullable=False)
    author_avatar_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )


class LibraryTag(Base):
    __tablename__ = "library_tag"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    tone: Mapped[str] = mapped_column(String(64), nullable=False)
    sort_order: Mapped[int | None] = mapped_column(Integer, nullable=True)


class LibraryArticleTag(Base):
    __tablename__ = "library_article_tag"
    __table_args__ = (Index("ix_library_article_tag_tag_id", "tag_id"),)

    article_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("library_article.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("library_tag.id", ondelete="RESTRICT"),
        primary_key=True,
    )
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )


class LibraryCourse(Base):
    """Каталог курсов (импорт из CSV и т.п.); отдельно от витрины library_showcase_item."""

    __tablename__ = "library_course"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    visibility: Mapped[str | None] = mapped_column(String(32), nullable=True)
    sphere: Mapped[str | None] = mapped_column(String(128), nullable=True)
    course_format: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    short_description: Mapped[str] = mapped_column(Text, nullable=False)
    learning_outcomes: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty_level: Mapped[str | None] = mapped_column(String(64), nullable=True)
    duration_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    modules_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lessons_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    practice_format: Mapped[str | None] = mapped_column(Text, nullable=True)
    mentor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    primary_skill: Mapped[str | None] = mapped_column(String(128), nullable=True)
    related_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    course_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    certificate: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    last_activity_days_ago: Mapped[int | None] = mapped_column(Integer, nullable=True)


class LibraryInterestTag(Base):
    """Maps catalog interests to tags; article interestIds are derived via article tags."""

    __tablename__ = "library_interest_tag"
    __table_args__ = (Index("ix_library_interest_tag_tag_id", "tag_id"),)

    interest_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("library_interest_option.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("library_tag.id", ondelete="CASCADE"),
        primary_key=True,
    )

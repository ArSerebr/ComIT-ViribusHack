from __future__ import annotations

import uuid
from typing import Any

from app.core.db.base import Base
from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column


class ProjectsColumn(Base):
    __tablename__ = "projects_column"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )


class ProjectsProject(Base):
    __tablename__ = "projects_project"
    __table_args__ = (Index("ix_projects_project_column_sort", "column_id", "sort_order"),)

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    team_name: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_label: Mapped[str] = mapped_column(String(255), nullable=False)
    team_avatar_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    details_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    visibility: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_hot: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    column_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("projects_column.id", ondelete="RESTRICT"),
        nullable=False,
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )


class ProjectsProjectDetail(Base):
    __tablename__ = "projects_project_detail"

    project_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("projects_project.id", ondelete="CASCADE"),
        primary_key=True,
    )
    owner_name: Mapped[str] = mapped_column(String(255), nullable=False)
    join_label: Mapped[str] = mapped_column(String(255), nullable=False)
    team_caption: Mapped[str] = mapped_column(String(255), nullable=False)
    productivity_caption: Mapped[str] = mapped_column(String(255), nullable=False)
    progress_caption: Mapped[str] = mapped_column(String(255), nullable=False)
    todo_caption: Mapped[str] = mapped_column(String(255), nullable=False)
    integration_caption: Mapped[str] = mapped_column(String(255), nullable=False)
    detail_blocks: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

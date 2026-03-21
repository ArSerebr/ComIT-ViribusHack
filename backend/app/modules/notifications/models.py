from __future__ import annotations

from sqlalchemy import Boolean, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import Base


class NotificationsItem(Base):
    __tablename__ = "notifications_item"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    date_label: Mapped[str] = mapped_column(String(255), nullable=False)
    date_caption: Mapped[str] = mapped_column(String(255), nullable=False)
    unread: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    author_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    accent_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cta_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    path: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

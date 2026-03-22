"""ORM для каталога сущностей персональных рекомендаций (проекты, курсы, статьи, хакатоны)."""

from __future__ import annotations

from datetime import datetime

from app.core.db.base import Base
from sqlalchemy import Boolean, DateTime, Integer, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column


class RecommendationCatalogItem(Base):
    """Единая таблица карточек для ML card_id и API RecommendationCard."""

    __tablename__ = "recommendation_catalog"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    kind: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    subtitle: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    link_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    topics: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

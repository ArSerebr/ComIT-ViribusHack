from __future__ import annotations

from typing import Any

from sqlalchemy import Integer, SmallInteger, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import Base


class DashboardRecommendation(Base):
    __tablename__ = "dashboard_recommendation"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    subtitle: Mapped[str] = mapped_column(Text, nullable=False)
    image: Mapped[str] = mapped_column(String(2048), nullable=False)
    link: Mapped[str] = mapped_column(String(2048), nullable=False)
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )


class DashboardHomeSnapshot(Base):
    """Singleton row (id=1) holding aggregated home dashboard JSON."""

    __tablename__ = "dashboard_home_snapshot"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    home_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

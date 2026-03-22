"""it_news_item — внешние IT-новости (RSS)

Revision ID: h3a4b5c6d7e8
Revises: g2b3c4d5e6f7
Create Date: 2026-03-22

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "h3a4b5c6d7e8"
down_revision: str | Sequence[str] | None = "g2b3c4d5e6f7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "it_news_item",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.String(64), nullable=False),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source", "external_id", name="uq_it_news_source_external_id"),
    )
    op.create_index("ix_it_news_item_source", "it_news_item", ["source"], unique=False)
    op.create_index(
        "ix_it_news_item_published_at",
        "it_news_item",
        ["published_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_it_news_item_published_at", table_name="it_news_item")
    op.drop_index("ix_it_news_item_source", table_name="it_news_item")
    op.drop_table("it_news_item")

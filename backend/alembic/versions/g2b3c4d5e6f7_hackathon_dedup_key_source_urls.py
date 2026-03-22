"""dedup_key and source_urls for hackathon deduplication

Revision ID: g2b3c4d5e6f7
Revises: f1a2b3c4d5e6
Create Date: 2026-03-22

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "g2b3c4d5e6f7"
down_revision: str | Sequence[str] | None = "f1a2b3c4d5e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "hackathon",
        sa.Column("dedup_key", sa.String(128), nullable=True),
    )
    op.add_column(
        "hackathon",
        sa.Column("source_urls", postgresql.JSONB(), nullable=True),
    )
    op.create_index(
        "ix_hackathon_dedup_key",
        "hackathon",
        ["dedup_key"],
        unique=False,
    )
    # Заполняем dedup_key для существующих записей (md5 от title+date)
    op.execute(
        """
        UPDATE hackathon SET dedup_key = MD5(LOWER(TRIM(title)) || '|' || COALESCE(start_date, ''))
        WHERE dedup_key IS NULL
        """
    )


def downgrade() -> None:
    op.drop_index("ix_hackathon_dedup_key", table_name="hackathon")
    op.drop_column("hackathon", "source_urls")
    op.drop_column("hackathon", "dedup_key")

"""news_featured_participant

Revision ID: a1b2c3d4e5f6
Revises: d5e6f7a8b9c0
Create Date: 2026-03-22

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "d5e6f7a8b9c0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "news_featured_participant",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("featured_id", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["featured_id"],
            ["news_featured.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", "featured_id"),
    )


def downgrade() -> None:
    op.drop_table("news_featured_participant")

"""library_interest_tag interest-to-tag mapping

Revision ID: c2d4e8f0a1b2
Revises: b1c2d3e4f5a6
Create Date: 2026-03-21

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c2d4e8f0a1b2"
down_revision: str | Sequence[str] | None = "b1c2d3e4f5a6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "library_interest_tag",
        sa.Column("interest_id", sa.String(length=64), nullable=False),
        sa.Column("tag_id", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(
            ["interest_id"],
            ["library_interest_option.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["library_tag.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("interest_id", "tag_id"),
    )
    op.create_index(
        "ix_library_interest_tag_tag_id",
        "library_interest_tag",
        ["tag_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_library_interest_tag_tag_id", table_name="library_interest_tag")
    op.drop_table("library_interest_tag")

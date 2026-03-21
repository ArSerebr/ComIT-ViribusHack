"""user_profile tables

Revision ID: 8f3a9c1e2b04
Revises: 7c2b9a1a2f4d
Create Date: 2026-03-21

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "8f3a9c1e2b04"
down_revision: str | Sequence[str] | None = "7c2b9a1a2f4d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_profile",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_table(
        "user_profile_interest",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("interest_id", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["interest_id"], ["library_interest_option.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("user_id", "interest_id"),
    )
    op.create_index(
        "ix_user_profile_interest_interest_id",
        "user_profile_interest",
        ["interest_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_user_profile_interest_interest_id", table_name="user_profile_interest")
    op.drop_table("user_profile_interest")
    op.drop_table("user_profile")

"""profile_university table and user_profile.university_id

Revision ID: d5e6f7a8b9c0
Revises: c2d4e8f0a1b2
Create Date: 2026-03-21

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d5e6f7a8b9c0"
down_revision: str | Sequence[str] | None = "c2d4e8f0a1b2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "profile_university",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column(
        "user_profile",
        sa.Column("university_id", sa.String(length=64), nullable=True),
    )
    op.create_foreign_key(
        "fk_user_profile_university_id_profile_university",
        "user_profile",
        "profile_university",
        ["university_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_user_profile_university_id",
        "user_profile",
        ["university_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_user_profile_university_id", table_name="user_profile")
    op.drop_constraint(
        "fk_user_profile_university_id_profile_university",
        "user_profile",
        type_="foreignkey",
    )
    op.drop_column("user_profile", "university_id")
    op.drop_table("profile_university")

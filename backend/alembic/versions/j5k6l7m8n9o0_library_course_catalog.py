"""library_course — каталог курсов из CSV/импорта

Revision ID: j5k6l7m8n9o0
Revises: i4a5b6c7d8e9
Create Date: 2026-03-22

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "j5k6l7m8n9o0"
down_revision: str | Sequence[str] | None = "i4a5b6c7d8e9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "library_course",
        sa.Column("id", sa.String(64), nullable=False),
        sa.Column("code", sa.String(32), nullable=False),
        sa.Column("visibility", sa.String(32), nullable=True),
        sa.Column("sphere", sa.String(128), nullable=True),
        sa.Column("course_format", sa.String(255), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("short_description", sa.Text(), nullable=False),
        sa.Column("learning_outcomes", sa.Text(), nullable=True),
        sa.Column("difficulty_level", sa.String(64), nullable=True),
        sa.Column("duration_hours", sa.Integer(), nullable=True),
        sa.Column("modules_count", sa.Integer(), nullable=True),
        sa.Column("lessons_count", sa.Integer(), nullable=True),
        sa.Column("practice_format", sa.Text(), nullable=True),
        sa.Column("mentor_name", sa.String(255), nullable=True),
        sa.Column("primary_skill", sa.String(128), nullable=True),
        sa.Column("related_skills", sa.Text(), nullable=True),
        sa.Column("course_status", sa.String(64), nullable=True),
        sa.Column("certificate", sa.Boolean(), nullable=True),
        sa.Column("last_activity_days_ago", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("library_course")

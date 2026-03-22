"""agent_demo_course_enrollment — демо-запись на курс (агент)

Revision ID: i4a5b6c7d8e9
Revises: h3a4b5c6d7e8
Create Date: 2026-03-22

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "i4a5b6c7d8e9"
down_revision: str | Sequence[str] | None = "h3a4b5c6d7e8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "agent_demo_course_enrollment",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("course_slug", sa.String(128), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_agent_demo_course_enrollment_user_id",
        "agent_demo_course_enrollment",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_agent_demo_course_enrollment_user_id", table_name="agent_demo_course_enrollment")
    op.drop_table("agent_demo_course_enrollment")

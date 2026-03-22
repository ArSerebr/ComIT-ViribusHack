"""hackathon table for parsed hackathon events

Revision ID: f1a2b3c4d5e6
Revises: e7f8a9b0c1d2
Create Date: 2026-03-22

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f1a2b3c4d5e6"
down_revision: str | Sequence[str] | None = "e7f8a9b0c1d2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "hackathon",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("description_raw", sa.Text(), nullable=True),
        sa.Column("start_date", sa.String(30), nullable=True),
        sa.Column("end_date", sa.String(30), nullable=True),
        sa.Column("registration_deadline", sa.String(30), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("is_online", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("prize_pool", sa.String(255), nullable=True),
        sa.Column("url", sa.String(2048), nullable=True),
        sa.Column("image_url", sa.String(2048), nullable=True),
        sa.Column("organizer", sa.String(255), nullable=True),
        sa.Column("tags", postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.String(20), server_default=sa.text("'upcoming'"), nullable=False),
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
        sa.UniqueConstraint("source", "external_id", name="uq_hackathon_source_external_id"),
    )
    op.create_index(
        "ix_hackathon_external_id",
        "hackathon",
        ["external_id"],
        unique=False,
    )
    op.create_index(
        "ix_hackathon_source",
        "hackathon",
        ["source"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_hackathon_source", table_name="hackathon")
    op.drop_index("ix_hackathon_external_id", table_name="hackathon")
    op.drop_table("hackathon")

"""recommendation_catalog — каталог для ML card_id и карточек главной

Revision ID: k6l7m8n9o0p1
Revises: j5k6l7m8n9o0
Create Date: 2026-03-22

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "k6l7m8n9o0p1"
down_revision: str | Sequence[str] | None = "j5k6l7m8n9o0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "recommendation_catalog",
        sa.Column("id", sa.String(length=255), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("subtitle", sa.Text(), nullable=False),
        sa.Column("image_url", sa.String(length=2048), nullable=False),
        sa.Column("link_url", sa.String(length=2048), nullable=False),
        sa.Column("topics", sa.Text(), nullable=True),
        sa.Column("skills", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_recommendation_catalog_kind",
        "recommendation_catalog",
        ["kind"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_recommendation_catalog_kind", table_name="recommendation_catalog")
    op.drop_table("recommendation_catalog")

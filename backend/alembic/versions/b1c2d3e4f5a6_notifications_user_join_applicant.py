"""notifications_item per-user PK; analytics_join_request applicant_user_id

Revision ID: b1c2d3e4f5a6
Revises: 9e4b1d7a3c55
Create Date: 2026-03-21

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b1c2d3e4f5a6"
down_revision: str | Sequence[str] | None = "9e4b1d7a3c55"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "notifications_item",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.execute(
        sa.text(
            """
            UPDATE notifications_item
            SET user_id = (SELECT id FROM "user" ORDER BY email LIMIT 1)
            WHERE EXISTS (SELECT 1 FROM "user")
            """
        )
    )
    op.execute(sa.text("DELETE FROM notifications_item WHERE user_id IS NULL"))
    op.alter_column(
        "notifications_item",
        "user_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
    op.drop_constraint("notifications_item_pkey", "notifications_item", type_="primary")
    op.create_primary_key(
        "notifications_item_pkey",
        "notifications_item",
        ["user_id", "id"],
    )
    op.create_foreign_key(
        "fk_notifications_item_user_id_user",
        "notifications_item",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_notifications_item_user_id_sort",
        "notifications_item",
        ["user_id", "sort_order", "id"],
        unique=False,
    )

    op.add_column(
        "analytics_join_request",
        sa.Column("applicant_user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index(
        "ix_analytics_join_request_applicant_user_id",
        "analytics_join_request",
        ["applicant_user_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_analytics_join_request_applicant_user_id_user",
        "analytics_join_request",
        "user",
        ["applicant_user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_analytics_join_request_applicant_user_id_user",
        "analytics_join_request",
        type_="foreignkey",
    )
    op.drop_index(
        "ix_analytics_join_request_applicant_user_id",
        table_name="analytics_join_request",
    )
    op.drop_column("analytics_join_request", "applicant_user_id")

    # Составной PK (user_id, id) при откате мог дать дубликаты id — очищаем таблицу.
    op.execute(sa.text("TRUNCATE notifications_item"))
    op.drop_index("ix_notifications_item_user_id_sort", table_name="notifications_item")
    op.drop_constraint(
        "fk_notifications_item_user_id_user",
        "notifications_item",
        type_="foreignkey",
    )
    op.drop_constraint("notifications_item_pkey", "notifications_item", type_="primary")
    op.create_primary_key("notifications_item_pkey", "notifications_item", ["id"])
    op.drop_column("notifications_item", "user_id")

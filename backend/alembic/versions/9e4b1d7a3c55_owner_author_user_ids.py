"""owner_user_id / author_user_id for projects, library, news

Revision ID: 9e4b1d7a3c55
Revises: 8f3a9c1e2b04
Create Date: 2026-03-21

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "9e4b1d7a3c55"
down_revision: str | Sequence[str] | None = "8f3a9c1e2b04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "projects_project",
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index(
        "ix_projects_project_owner_user_id",
        "projects_project",
        ["owner_user_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_projects_project_owner_user_id_user",
        "projects_project",
        "user",
        ["owner_user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column(
        "library_article",
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index(
        "ix_library_article_owner_user_id",
        "library_article",
        ["owner_user_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_library_article_owner_user_id_user",
        "library_article",
        "user",
        ["owner_user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column(
        "news_mini",
        sa.Column("author_user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index(
        "ix_news_mini_author_user_id",
        "news_mini",
        ["author_user_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_news_mini_author_user_id_user",
        "news_mini",
        "user",
        ["author_user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column(
        "news_featured",
        sa.Column("author_user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index(
        "ix_news_featured_author_user_id",
        "news_featured",
        ["author_user_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_news_featured_author_user_id_user",
        "news_featured",
        "user",
        ["author_user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_news_featured_author_user_id_user", "news_featured", type_="foreignkey")
    op.drop_index("ix_news_featured_author_user_id", table_name="news_featured")
    op.drop_column("news_featured", "author_user_id")

    op.drop_constraint("fk_news_mini_author_user_id_user", "news_mini", type_="foreignkey")
    op.drop_index("ix_news_mini_author_user_id", table_name="news_mini")
    op.drop_column("news_mini", "author_user_id")

    op.drop_constraint(
        "fk_library_article_owner_user_id_user", "library_article", type_="foreignkey"
    )
    op.drop_index("ix_library_article_owner_user_id", table_name="library_article")
    op.drop_column("library_article", "owner_user_id")

    op.drop_constraint(
        "fk_projects_project_owner_user_id_user", "projects_project", type_="foreignkey"
    )
    op.drop_index("ix_projects_project_owner_user_id", table_name="projects_project")
    op.drop_column("projects_project", "owner_user_id")

"""init

Revision ID: ef5b4a366db3
Revises:
Create Date: 2025-02-04 15:17:01.961739

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "ef5b4a366db3"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "category",
        sa.Column("codename", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.Column("aliases", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("is_base_expense", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_category")),
        sa.UniqueConstraint("codename", name=op.f("uq_category_codename")),
    )
    op.create_table(
        "user",
        sa.Column("telegram_id", sa.Integer(), nullable=False),
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.Column("lastname", sa.String(length=32), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user")),
        sa.UniqueConstraint("chat_id", name=op.f("uq_user_chat_id")),
        sa.UniqueConstraint("telegram_id", name=op.f("uq_user_telegram_id")),
    )
    op.create_table(
        "assets",
        sa.Column("codename", sa.String(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], name=op.f("fk_assets_user_id_user")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_assets")),
    )
    op.create_table(
        "expense",
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["category.id"], name=op.f("fk_expense_category_id_category")),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], name=op.f("fk_expense_user_id_user")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_expense")),
    )


def downgrade() -> None:
    op.drop_table("expense")
    op.drop_table("assets")
    op.drop_table("user")
    op.drop_table("category")

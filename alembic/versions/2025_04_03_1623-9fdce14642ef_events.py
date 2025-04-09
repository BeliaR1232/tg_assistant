"""events

Revision ID: 9fdce14642ef
Revises: ef5b4a366db3
Create Date: 2025-04-03 16:23:37.488150

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "9fdce14642ef"
down_revision: Union[str, None] = "ef5b4a366db3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sa.Enum("DAILY", "WEEKLY", "MONTHLY", "YEARLY", name="event_repeat_intervals").create(op.get_bind())
    op.create_table(
        "event",
        sa.Column("event_datetime", sa.DateTime(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "repeat_interval",
            postgresql.ENUM("DAILY", "WEEKLY", "MONTHLY", "YEARLY", name="event_repeat_intervals", create_type=False),
            nullable=True,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], name=op.f("fk_event_user_id_user")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_event")),
    )


def downgrade() -> None:
    op.drop_table("event")
    sa.Enum("DAILY", "WEEKLY", "MONTHLY", "YEARLY", name="event_repeat_intervals").drop(op.get_bind())

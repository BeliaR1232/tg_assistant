"""add event.message_count

Revision ID: c7b72be727f2
Revises: 9fdce14642ef
Create Date: 2025-04-07 12:40:51.714614

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "c7b72be727f2"
down_revision: Union[str, None] = "9fdce14642ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("event", sa.Column("message_count", sa.Integer(), nullable=False))


def downgrade() -> None:
    op.drop_column("event", "message_count")

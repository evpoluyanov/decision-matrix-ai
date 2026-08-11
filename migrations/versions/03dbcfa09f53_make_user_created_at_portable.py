"""make user created_at portable

Revision ID: 03dbcfa09f53
Revises: 7f3c85b36ab0
Create Date: 2026-08-11 14:34:52.488886

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '03dbcfa09f53'
down_revision: Union[str, Sequence[str], None] = '7f3c85b36ab0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Используем стандартный SQL CURRENT_TIMESTAMP,
    который поддерживают PostgreSQL и SQLite.
    """
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )


def downgrade() -> None:
    """
    Возвращаем предыдущий вариант значения по умолчанию.
    """
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
            server_default=sa.text("now()"),
        )
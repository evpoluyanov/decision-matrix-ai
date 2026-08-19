"""add email verification status

Revision ID: 663edc576004
Revises: 8034db4af01b
Create Date: 2026-08-18 19:57:41.417484
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "663edc576004"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "8034db4af01b"

branch_labels: Union[
    str,
    Sequence[str],
    None,
] = None

depends_on: Union[
    str,
    Sequence[str],
    None,
] = None


def upgrade() -> None:
    """
    Добавляет признак подтверждения email.

    Существующие пользователи считаются
    уже подтвердившими свои адреса.
    """
    with op.batch_alter_table(
        "users"
    ) as batch_op:
        batch_op.add_column(
            sa.Column(
                "email_verified",
                sa.Boolean(),
                nullable=True,
            )
        )

    op.execute(
        sa.text(
            """
            UPDATE users
            SET email_verified = TRUE
            WHERE email_verified IS NULL
            """
        )
    )

    with op.batch_alter_table(
        "users"
    ) as batch_op:
        batch_op.alter_column(
            "email_verified",
            existing_type=sa.Boolean(),
            existing_nullable=True,
            nullable=False,
        )


def downgrade() -> None:
    """
    Удаляет признак подтверждения email
    при откате миграции.
    """
    with op.batch_alter_table(
        "users"
    ) as batch_op:
        batch_op.drop_column(
            "email_verified"
        )
"""require project owner

Revision ID: 9d7a2c6f4b81
Revises: 03dbcfa09f53
Create Date: 2026-08-12
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9d7a2c6f4b81"
down_revision: Union[str, Sequence[str], None] = "03dbcfa09f53"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()

    orphan_project_count = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM projects
            WHERE owner_id IS NULL
            """
        )
    ).scalar_one()

    if orphan_project_count > 0:
        user_count = connection.execute(
            sa.text(
                """
                SELECT COUNT(*)
                FROM users
                """
            )
        ).scalar_one()

        if user_count != 1:
            raise RuntimeError(
                "Невозможно автоматически назначить владельцев: "
                "есть проекты без владельца, а количество "
                "пользователей не равно одному."
            )

        owner_id = connection.execute(
            sa.text(
                """
                SELECT id
                FROM users
                LIMIT 1
                """
            )
        ).scalar_one()

        connection.execute(
            sa.text(
                """
                UPDATE projects
                SET owner_id = :owner_id
                WHERE owner_id IS NULL
                """
            ),
            {"owner_id": owner_id},
        )

    remaining_orphans = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM projects
            WHERE owner_id IS NULL
            """
        )
    ).scalar_one()

    if remaining_orphans != 0:
        raise RuntimeError(
            "После миграции остались проекты без владельца."
        )

    with op.batch_alter_table("projects") as batch_op:
        batch_op.alter_column(
            "owner_id",
            existing_type=sa.Integer(),
            nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("projects") as batch_op:
        batch_op.alter_column(
            "owner_id",
            existing_type=sa.Integer(),
            nullable=True,
        )
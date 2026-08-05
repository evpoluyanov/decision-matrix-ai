"""add users and project ownership

Revision ID: 7f3c85b36ab0
Revises: afc74d232cae
Create Date: 2026-08-05 12:54:05.514773

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Уникальный идентификатор этой миграции.
revision: str = "7f3c85b36ab0"

# Предыдущая миграция, от которой продолжается история базы.
down_revision: Union[str, Sequence[str], None] = "afc74d232cae"

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Переход к новой версии базы.

    Создаём таблицу пользователей и добавляем владельца проекта.
    """

    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(length=320),
            nullable=False,
        ),
        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=True,
    )

    with op.batch_alter_table("projects") as batch_op:
        batch_op.add_column(
            sa.Column(
                "owner_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.create_index(
            "ix_projects_owner_id",
            ["owner_id"],
            unique=False,
        )

        batch_op.create_foreign_key(
            "fk_projects_owner_id_users",
            "users",
            ["owner_id"],
            ["id"],
        )


def downgrade() -> None:
    """
    Возврат к предыдущей версии базы.

    Удаляем владельца проекта и таблицу пользователей.
    """

    with op.batch_alter_table("projects") as batch_op:
        batch_op.drop_constraint(
            "fk_projects_owner_id_users",
            type_="foreignkey",
        )

        batch_op.drop_index(
            "ix_projects_owner_id",
        )

        batch_op.drop_column(
            "owner_id",
        )

    op.drop_index(
        "ix_users_email",
        table_name="users",
    )

    op.drop_table(
        "users",
    )
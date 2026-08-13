"""Add AI assistant data.

Revision ID: 6b2f0d4a8c91
Revises: 9d7a2c6f4b81
Create Date: 2026-08-13
"""

from alembic import op
import sqlalchemy as sa


revision = "6b2f0d4a8c91"
down_revision = "9d7a2c6f4b81"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "projects",
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "alternatives",
        sa.Column(
            "ai_suggested_name",
            sa.String(),
            nullable=True,
        ),
    )

    op.add_column(
        "alternatives",
        sa.Column(
            "ai_explanation",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "criteria",
        sa.Column(
            "ai_suggested_name",
            sa.String(),
            nullable=True,
        ),
    )

    op.add_column(
        "criteria",
        sa.Column(
            "ai_suggested_weight",
            sa.Float(),
            nullable=True,
        ),
    )

    op.add_column(
        "criteria",
        sa.Column(
            "ai_criterion_explanation",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "criteria",
        sa.Column(
            "ai_weight_explanation",
            sa.Text(),
            nullable=True,
        ),
    )

    with op.batch_alter_table("scores") as batch_op:
        batch_op.alter_column(
            "value",
            existing_type=sa.Float(),
            nullable=True,
        )

        batch_op.add_column(
            sa.Column(
                "ai_value",
                sa.Float(),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "ai_explanation",
                sa.Text(),
                nullable=True,
            )
        )


def downgrade():
    connection = op.get_bind()

    unconfirmed_scores = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM scores
            WHERE value IS NULL
            """
        )
    ).scalar_one()

    if unconfirmed_scores > 0:
        raise RuntimeError(
            "Невозможно безопасно откатить миграцию: "
            "есть оценки без подтверждённого "
            "пользовательского значения."
        )

    with op.batch_alter_table("scores") as batch_op:
        batch_op.drop_column(
            "ai_explanation"
        )

        batch_op.drop_column(
            "ai_value"
        )

        batch_op.alter_column(
            "value",
            existing_type=sa.Float(),
            nullable=False,
        )

    op.drop_column(
        "criteria",
        "ai_weight_explanation",
    )

    op.drop_column(
        "criteria",
        "ai_criterion_explanation",
    )

    op.drop_column(
        "criteria",
        "ai_suggested_weight",
    )

    op.drop_column(
        "criteria",
        "ai_suggested_name",
    )

    op.drop_column(
        "alternatives",
        "ai_explanation",
    )

    op.drop_column(
        "alternatives",
        "ai_suggested_name",
    )

    op.drop_column(
        "projects",
        "description",
    )
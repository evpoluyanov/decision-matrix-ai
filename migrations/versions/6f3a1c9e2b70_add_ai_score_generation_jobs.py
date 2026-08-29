"""Add resumable AI score generation jobs.

Revision ID: 6f3a1c9e2b70
Revises: c9a7f431b2d0
"""

from alembic import op
import sqlalchemy as sa


revision = "6f3a1c9e2b70"
down_revision = "c9a7f431b2d0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "ai_score_generation_jobs",
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("request_log_id", sa.Integer(), nullable=False),
        sa.Column("alternative_ids_json", sa.Text(), nullable=False),
        sa.Column("criterion_ids_json", sa.Text(), nullable=False),
        sa.Column("next_alternative_index", sa.Integer(), nullable=False),
        sa.Column("provider_attempts", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("last_error_code", sa.String(50), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False,
        ),
        sa.CheckConstraint(
            "next_alternative_index >= 0",
            name="ck_ai_score_job_progress_nonnegative",
        ),
        sa.CheckConstraint(
            "provider_attempts >= 0",
            name="ck_ai_score_job_attempts_nonnegative",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["request_log_id"], ["ai_request_logs.id"], ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("project_id"),
        sa.UniqueConstraint("request_log_id"),
    )


def downgrade():
    op.drop_table("ai_score_generation_jobs")

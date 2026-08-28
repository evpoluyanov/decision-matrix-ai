"""Add durable auth throttles and AI money reservations.

Revision ID: c9a7f431b2d0
Revises: 89b807e95fe4
"""
from alembic import op
import sqlalchemy as sa

revision = "c9a7f431b2d0"
down_revision = "89b807e95fe4"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "auth_rate_limits",
        sa.Column("key", sa.String(64), primary_key=True),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_auth_rate_limits_expires_at", "auth_rate_limits", ["expires_at"])
    op.create_table(
        "ai_daily_budgets",
        sa.Column("day", sa.Date(), primary_key=True),
        sa.Column("allocated_microrub", sa.BigInteger(), nullable=False),
        sa.CheckConstraint("allocated_microrub >= 0", name="ck_ai_budget_nonnegative"),
    )
    op.create_table(
        "ai_provider_calls",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_log_id", sa.Integer(),
                  sa.ForeignKey("ai_request_logs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("budget_day", sa.Date(), sa.ForeignKey("ai_daily_budgets.day"), nullable=False),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("input_rub_per_million", sa.Numeric(14, 6), nullable=False),
        sa.Column("output_rub_per_million", sa.Numeric(14, 6), nullable=False),
        sa.Column("input_token_bound", sa.Integer(), nullable=False),
        sa.Column("output_token_bound", sa.Integer(), nullable=False),
        sa.Column("reserved_microrub", sa.BigInteger(), nullable=False),
        sa.Column("charged_microrub", sa.BigInteger(), nullable=False),
        sa.Column("estimated_microrub", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("reasoning_tokens", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("charged_microrub >= 0", name="ck_ai_call_nonnegative"),
    )
    op.create_index("ix_ai_provider_calls_request_log_id", "ai_provider_calls", ["request_log_id"])
    op.create_index("ix_ai_provider_calls_budget_day", "ai_provider_calls", ["budget_day"])
    op.create_index("ix_ai_provider_calls_created_at", "ai_provider_calls", ["created_at"])


def downgrade():
    # Destructive for new billing history; never run on production casually.
    op.drop_index("ix_ai_provider_calls_created_at", table_name="ai_provider_calls")
    op.drop_index("ix_ai_provider_calls_budget_day", table_name="ai_provider_calls")
    op.drop_index("ix_ai_provider_calls_request_log_id", table_name="ai_provider_calls")
    op.drop_table("ai_provider_calls")
    op.drop_table("ai_daily_budgets")
    op.drop_index("ix_auth_rate_limits_expires_at", table_name="auth_rate_limits")
    op.drop_table("auth_rate_limits")

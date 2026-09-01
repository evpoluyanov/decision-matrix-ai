"""Add growth experiment, feedback and MWS reconciliation data.

Revision ID: b7e2c4d91a63
Revises: 6f3a1c9e2b70
"""

from alembic import op
import sqlalchemy as sa


revision = "b7e2c4d91a63"
down_revision = "6f3a1c9e2b70"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("projects") as batch_op:
        batch_op.add_column(sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False,
        ))

    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column(
            "beta_reward_eligible", sa.Boolean(), server_default=sa.false(), nullable=False,
        ))
        batch_op.add_column(sa.Column(
            "beta_reward_eligible_at", sa.DateTime(timezone=True), nullable=True,
        ))
        batch_op.add_column(sa.Column("beta_reward_reason", sa.String(100), nullable=True))
        batch_op.add_column(sa.Column(
            "beta_reward_granted", sa.Boolean(), server_default=sa.false(), nullable=False,
        ))

    with op.batch_alter_table("ai_request_logs") as batch_op:
        batch_op.add_column(sa.Column("provider", sa.String(30), nullable=True))
        batch_op.add_column(sa.Column("model", sa.String(100), nullable=True))
        batch_op.add_column(sa.Column("provider_response_id", sa.String(255), nullable=True))

    op.create_table(
        "monetization_preferences",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("selected_plan", sa.String(30), nullable=False),
        sa.Column("notify_on_launch", sa.Boolean(), nullable=False),
        sa.Column("source", sa.String(30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index(
        "ix_monetization_preferences_user_id", "monetization_preferences",
        ["user_id"], unique=True,
    )

    op.create_table(
        "product_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_name", sa.String(50), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=False),
        sa.Column("dedupe_key", sa.String(160), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.UniqueConstraint("dedupe_key"),
    )
    op.create_index("ix_product_events_user_id", "product_events", ["user_id"])
    op.create_index("ix_product_events_project_id", "product_events", ["project_id"])
    op.create_index("ix_product_events_name_created_at", "product_events", ["event_name", "created_at"])

    op.create_table(
        "user_attributions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("utm_source", sa.String(200), nullable=True),
        sa.Column("utm_medium", sa.String(200), nullable=True),
        sa.Column("utm_campaign", sa.String(200), nullable=True),
        sa.Column("utm_content", sa.String(200), nullable=True),
        sa.Column("referrer", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index(
        "ix_user_attributions_user_id", "user_attributions", ["user_id"], unique=True,
    )

    op.create_table(
        "user_feedback",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="SET NULL"), nullable=True),
        sa.Column("category", sa.String(30), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("page_path", sa.String(500), nullable=False),
        sa.Column("allow_email_reply", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("admin_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("rating IS NULL OR (rating >= 1 AND rating <= 5)", name="ck_feedback_rating"),
    )
    op.create_index("ix_user_feedback_user_id", "user_feedback", ["user_id"])
    op.create_index("ix_user_feedback_project_id", "user_feedback", ["project_id"])
    op.create_index("ix_user_feedback_status_created_at", "user_feedback", ["status", "created_at"])

    op.create_table(
        "mws_billing_reconciliations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("input_tokens", sa.BigInteger(), nullable=False),
        sa.Column("output_tokens", sa.BigInteger(), nullable=False),
        sa.Column("actual_base_cost_rub", sa.Numeric(14, 6), nullable=False),
        sa.Column("discount_or_grant_rub", sa.Numeric(14, 6), nullable=False),
        sa.Column("amount_due_rub", sa.Numeric(14, 6), nullable=False),
        sa.Column("application_estimated_cost_rub", sa.Numeric(14, 6), nullable=False),
        sa.Column("deviation_rub", sa.Numeric(14, 6), nullable=False),
        sa.Column("source", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )


def downgrade():
    op.drop_table("mws_billing_reconciliations")
    op.drop_index("ix_user_feedback_status_created_at", table_name="user_feedback")
    op.drop_index("ix_user_feedback_project_id", table_name="user_feedback")
    op.drop_index("ix_user_feedback_user_id", table_name="user_feedback")
    op.drop_table("user_feedback")
    op.drop_index("ix_user_attributions_user_id", table_name="user_attributions")
    op.drop_table("user_attributions")
    op.drop_index("ix_product_events_name_created_at", table_name="product_events")
    op.drop_index("ix_product_events_project_id", table_name="product_events")
    op.drop_index("ix_product_events_user_id", table_name="product_events")
    op.drop_table("product_events")
    op.drop_index("ix_monetization_preferences_user_id", table_name="monetization_preferences")
    op.drop_table("monetization_preferences")
    with op.batch_alter_table("ai_request_logs") as batch_op:
        batch_op.drop_column("provider_response_id")
        batch_op.drop_column("model")
        batch_op.drop_column("provider")
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("beta_reward_granted")
        batch_op.drop_column("beta_reward_reason")
        batch_op.drop_column("beta_reward_eligible_at")
        batch_op.drop_column("beta_reward_eligible")
    with op.batch_alter_table("projects") as batch_op:
        batch_op.drop_column("created_at")

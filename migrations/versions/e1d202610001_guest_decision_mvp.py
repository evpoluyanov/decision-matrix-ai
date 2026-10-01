"""Guest decisions and consented journey cohorts; retain all legacy projects."""
from alembic import op
import sqlalchemy as sa
revision = "e1d202610001"
down_revision = "3a7d9c1e5b42"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("decision_journeys",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("source", sa.String(200)),
        sa.Column("analytics_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("decision_briefs",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("access_digest", sa.String(64), nullable=False),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("pending_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("journey_id", sa.String(64), sa.ForeignKey("decision_journeys.id", ondelete="SET NULL")),
        sa.Column("question", sa.Text(), nullable=False), sa.Column("details", sa.Text(), nullable=False),
        sa.Column("allow_suggestions", sa.Boolean(), nullable=False),
        sa.Column("understanding_json", sa.Text()), sa.Column("result_json", sa.Text()),
        sa.Column("state", sa.String(30), nullable=False), sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("operation_key", sa.String(64)), sa.Column("error_code", sa.String(50)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True)))
    for col in ("owner_id", "pending_user_id", "expires_at"):
        op.create_index("ix_decision_briefs_" + col, "decision_briefs", [col])
    with op.batch_alter_table("ai_request_logs") as batch:
        batch.alter_column("user_id", existing_type=sa.Integer(), nullable=True)
        batch.add_column(sa.Column("guest_identity", sa.String(64)))
        batch.create_index("ix_ai_request_logs_guest_identity", ["guest_identity"])


def downgrade():
    # Guest logs are technical evidence of charges; do not silently delete them.
    if op.get_bind().execute(sa.text("SELECT COUNT(*) FROM ai_request_logs WHERE user_id IS NULL")).scalar():
        raise RuntimeError("Guest AI logs exist; restore application code without dropping billing evidence.")
    with op.batch_alter_table("ai_request_logs") as batch:
        batch.drop_index("ix_ai_request_logs_guest_identity")
        batch.drop_column("guest_identity")
        batch.alter_column("user_id", existing_type=sa.Integer(), nullable=False)
    op.drop_table("decision_briefs")
    op.drop_table("decision_journeys")

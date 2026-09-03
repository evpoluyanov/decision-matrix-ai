"""Add operation identity and optimistic matrix revision (no new tables)."""
from alembic import op
import sqlalchemy as sa

revision = "d2f48ab17390"
down_revision = "b7e2c4d91a63"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("projects", sa.Column("matrix_revision", sa.Integer(), server_default=sa.text("0"), nullable=False))
    op.add_column("projects", sa.Column("last_matrix_save_key", sa.String(64), nullable=True))
    op.add_column("ai_score_generation_jobs", sa.Column("matrix_revision", sa.Integer(), nullable=True))
    op.add_column("ai_request_logs", sa.Column("client_request_key", sa.String(64), nullable=True))
    op.add_column("ai_request_logs", sa.Column("error_code", sa.String(50), nullable=True))
    with op.batch_alter_table("ai_request_logs") as batch:
        batch.create_unique_constraint("uq_ai_request_client_key", ["client_request_key"])


def downgrade():
    with op.batch_alter_table("ai_request_logs") as batch:
        batch.drop_constraint("uq_ai_request_client_key", type_="unique")
        batch.drop_column("error_code")
        batch.drop_column("client_request_key")
    op.drop_column("ai_score_generation_jobs", "matrix_revision")
    op.drop_column("projects", "last_matrix_save_key")
    op.drop_column("projects", "matrix_revision")

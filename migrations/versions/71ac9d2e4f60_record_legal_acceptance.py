"""Record the legal-document versions accepted during registration."""

from alembic import op
import sqlalchemy as sa


revision = "71ac9d2e4f60"
down_revision = "f4c912ab670e"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column(
            "terms_accepted_at", sa.DateTime(timezone=True), nullable=True,
        ))
        batch_op.add_column(sa.Column(
            "terms_version", sa.String(32), nullable=True,
        ))
        batch_op.add_column(sa.Column(
            "personal_data_consent_at", sa.DateTime(timezone=True), nullable=True,
        ))
        batch_op.add_column(sa.Column(
            "personal_data_consent_version", sa.String(32), nullable=True,
        ))


def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("personal_data_consent_version")
        batch_op.drop_column("personal_data_consent_at")
        batch_op.drop_column("terms_version")
        batch_op.drop_column("terms_accepted_at")

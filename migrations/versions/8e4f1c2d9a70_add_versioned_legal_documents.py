"""Add versioned legal documents and explicit confirmations.

No legacy document text or user acceptance is copied by this migration.
"""

from alembic import op
import sqlalchemy as sa


revision = "8e4f1c2d9a70"
down_revision = "71ac9d2e4f60"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "legal_document_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_key", sa.String(30), nullable=False),
        sa.Column("version", sa.String(32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("change_summary", sa.String(500), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"], ["users.id"], ondelete="SET NULL",
        ),
        sa.UniqueConstraint(
            "document_key", "version", name="uq_legal_document_key_version",
        ),
    )
    op.create_index(
        "ix_legal_document_key_status",
        "legal_document_versions",
        ["document_key", "status"],
    )
    op.create_table(
        "user_legal_acceptances",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("document_version_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column(
            "accepted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["document_version_id"],
            ["legal_document_versions.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "user_id",
            "document_version_id",
            name="uq_user_legal_document_acceptance",
        ),
    )
    op.create_index(
        "ix_user_legal_acceptance_user",
        "user_legal_acceptances",
        ["user_id"],
    )


def downgrade():
    op.drop_index(
        "ix_user_legal_acceptance_user", table_name="user_legal_acceptances",
    )
    op.drop_table("user_legal_acceptances")
    op.drop_index(
        "ix_legal_document_key_status", table_name="legal_document_versions",
    )
    op.drop_table("legal_document_versions")

"""Remember one report-helpfulness answer per user, without a new table."""
from alembic import op
import sqlalchemy as sa

revision = "f4c912ab670e"
down_revision = "d2f48ab17390"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user_feedback", sa.Column("question_key", sa.String(40), nullable=True))
    # Legacy records have no 'quick' flag. Preserve prior rated result-quality
    # feedback submitted from a report as an answer; keep every historical row.
    op.execute(sa.text("""
        UPDATE user_feedback SET question_key = 'report_helpfulness_v1'
        WHERE id IN (
            SELECT MIN(id) FROM user_feedback
            WHERE category = 'result_quality' AND rating BETWEEN 1 AND 5
              AND page_path LIKE '/projects/%/report'
            GROUP BY user_id
        )
    """))
    with op.batch_alter_table("user_feedback") as batch:
        batch.create_unique_constraint("uq_feedback_user_question", ["user_id", "question_key"])


def downgrade():
    with op.batch_alter_table("user_feedback") as batch:
        batch.drop_constraint("uq_feedback_user_question", type_="unique")
        batch.drop_column("question_key")

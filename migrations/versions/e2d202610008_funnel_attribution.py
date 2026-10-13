"""Keep consented first-touch attribution for anonymous funnel details."""
from alembic import op
import sqlalchemy as sa

revision = "e2d202610008"
down_revision = "e1d202610001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("decision_journeys", sa.Column("attribution_json", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("decision_journeys", "attribution_json")

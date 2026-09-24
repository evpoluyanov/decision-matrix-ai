"""Store user-facing criterion importance categories."""

from alembic import op
import sqlalchemy as sa


revision = "3a7d9c1e5b42"
down_revision = "8e4f1c2d9a70"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "criteria",
        sa.Column(
            "importance",
            sa.String(length=20),
            server_default="important",
            nullable=False,
        ),
    )
    op.execute(
        """
        UPDATE criteria
        SET importance = CASE
            WHEN weight >= 0.35 THEN 'critical'
            WHEN weight < 0.15 THEN 'desirable'
            ELSE 'important'
        END
        """
    )
    connection = op.get_bind()
    rows = connection.execute(
        sa.text(
            "SELECT id, project_id, importance "
            "FROM criteria ORDER BY project_id, id"
        )
    ).mappings().all()
    by_project = {}
    for row in rows:
        by_project.setdefault(row["project_id"], []).append(row)

    shares = {"critical": 0.60, "important": 0.30, "desirable": 0.10}
    for criteria in by_project.values():
        grouped = {
            key: [row for row in criteria if row["importance"] == key]
            for key in shares
        }
        active_share = sum(shares[key] for key, items in grouped.items() if items)
        weights = {}
        for key, items in grouped.items():
            if items:
                item_weight = (shares[key] / active_share) / len(items)
                for item in items:
                    weights[item["id"]] = item_weight
        if criteria:
            last_id = criteria[-1]["id"]
            weights[last_id] += 1.0 - sum(weights.values())
        connection.execute(
            sa.text("UPDATE criteria SET weight = :weight WHERE id = :id"),
            [{"id": item_id, "weight": weight} for item_id, weight in weights.items()],
        )

    # The streamlined flow treats AI-generated scores as the editable current
    # matrix instead of a separate unconfirmed layer.
    op.execute(
        "UPDATE scores SET value = ai_value "
        "WHERE value IS NULL AND ai_value IS NOT NULL"
    )


def downgrade():
    op.drop_column("criteria", "importance")

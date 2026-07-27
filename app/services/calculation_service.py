from sqlalchemy.orm import Session

from app.models import Alternative


def calculate_results(
    db: Session,
    project_id: int,
) -> list[dict]:
    alternatives = (
        db.query(Alternative)
        .filter_by(project_id=project_id)
        .all()
    )

    results = []

    for alternative in alternatives:
        total = 0.0
        contributions = {}

        for score in alternative.scores:
            contribution = round(
                score.value * score.criterion.weight,
                2,
            )

            contributions[score.criterion_id] = contribution
            total += contribution

        results.append(
            {
                "alternative": alternative,
                "contributions": contributions,
                "total": round(total, 2),
            }
        )

    results.sort(
        key=lambda item: item["total"],
        reverse=True,
    )

    return results
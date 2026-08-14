from sqlalchemy.orm import Session

from app.models import Alternative


def calculate_results(
    db: Session,
    project_id: int,
) -> list[dict]:
    alternatives = (
        db.query(Alternative)
        .filter_by(
            project_id=project_id
        )
        .all()
    )

    results = []

    for alternative in alternatives:
        total = 0.0
        contributions = {}
        has_scores = False

        for score in alternative.scores:
            effective_value = (
                score.value
                if score.value is not None
                else score.ai_value
            )

            if effective_value is None:
                continue

            has_scores = True

            contribution = round(
                effective_value
                * score.criterion.weight,
                2,
            )

            contributions[
                score.criterion_id
            ] = contribution

            total += contribution

        if has_scores:
            results.append(
                {
                    "alternative":
                        alternative,
                    "contributions":
                        contributions,
                    "total":
                        round(total, 2),
                }
            )

    results.sort(
        key=lambda item: item["total"],
        reverse=True,
    )

    return results
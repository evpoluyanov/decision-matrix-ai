from sqlalchemy.orm import Session

from app.models import Score


def set_score(
    db: Session,
    alternative_id: int,
    criterion_id: int,
    value: float,
) -> Score:
    score = (
        db.query(Score)
        .filter(
            Score.alternative_id == alternative_id,
            Score.criterion_id == criterion_id,
        )
        .first()
    )

    if score:
        score.value = value
    else:
        score = Score(
            alternative_id=alternative_id,
            criterion_id=criterion_id,
            value=value,
        )
        db.add(score)

    db.commit()
    db.refresh(score)

    return score
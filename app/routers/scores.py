from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import score_service


router = APIRouter()


@router.post("/projects/{project_id}/scores")
async def save_scores(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    form_data = await request.form()

    for field_name, raw_value in form_data.items():
        # Нас интересуют только поля вида:
        # score_1_2
        if not field_name.startswith("score_"):
            continue

        # Пустые ячейки не сохраняем
        if raw_value == "":
            continue

        parts = field_name.split("_")

        if len(parts) != 3:
            continue

        try:
            alternative_id = int(parts[1])
            criterion_id = int(parts[2])
            value = float(raw_value)
        except ValueError:
            continue

        # Дополнительная защита на стороне сервера
        if value < 0 or value > 10:
            continue

        score_service.set_score(
            db=db,
            alternative_id=alternative_id,
            criterion_id=criterion_id,
            value=value,
        )

    return RedirectResponse(
        url=f"/projects/{project_id}",
        status_code=303,
    )
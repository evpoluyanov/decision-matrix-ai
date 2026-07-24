from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import score_service

router = APIRouter()


@router.post("/projects/{project_id}/scores")
def save_score(
    project_id: int,
    alternative_id: int = Form(...),
    criterion_id: int = Form(...),
    value: float = Form(...),
    db: Session = Depends(get_db),
):
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
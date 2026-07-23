from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import criterion_service

router = APIRouter()


@router.post("/projects/{project_id}/criteria")
def create_criterion(
    project_id: int,
    name: str = Form(...),
    db: Session = Depends(get_db),
):
    criterion_service.create_criterion(
        db,
        project_id,
        name,
    )

    return RedirectResponse(
        url=f"/projects/{project_id}",
        status_code=303,
    )
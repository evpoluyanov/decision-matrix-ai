import re
from time import perf_counter
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app import models
from app.auth_dependencies import require_project_owner
from app.database import get_db
from app.services import score_service

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/projects/{project_id}/scores")
async def save_scores(project_id: int, request: Request, db: Session = Depends(get_db),
                      project: models.Project = Depends(require_project_owner)):
    form = await request.form()
    key = str(form.get("request_key", ""))
    if not re.fullmatch(r"[a-zA-Z0-9_-]{16,64}", key):
        key = None
    started = perf_counter()
    try:
        revision = score_service.save_matrix(db, project.id, form, form.get("matrix_revision"), key)
    except (score_service.MatrixSaveError, SQLAlchemyError) as exc:
        db.rollback()
        validation = isinstance(exc, score_service.MatrixSaveError)
        status = exc.status if validation else 503
        message = str(exc) if validation else "Не удалось подтвердить сохранение. Введённые значения остались на экране. Проверьте состояние перед повторной отправкой."
        data = {"status": "error", "message": message, "field": exc.field if validation else None}
        if request.headers.get("x-requested-with") == "fetch":
            return JSONResponse(data, status_code=status)
        return templates.TemplateResponse(request=request, name="matrix_save_error.html", status_code=status,
            context={"project": project, "message": message, "values": {k:v for k,v in form.items() if re.fullmatch(r"score_\d+_\d+", k)},
                     "matrix_revision": form.get("matrix_revision", ""), "request_key": key or ""})
    headers = {"Server-Timing": f"matrix_save;dur={(perf_counter()-started)*1000:.2f}"}
    if request.headers.get("x-requested-with") == "fetch":
        return JSONResponse({"status": "ok", "matrix_revision": revision, "message": "Матрица сохранена полностью."}, headers=headers)
    return RedirectResponse(f"/projects/{project.id}#matrix", status_code=303, headers=headers)


@router.get("/projects/{project_id}/scores/state")
def matrix_state(project_id: int, request_key: str = "", db: Session = Depends(get_db),
                 project: models.Project = Depends(require_project_owner)):
    return {"status": "saved" if request_key and project.last_matrix_save_key == request_key else "unconfirmed",
            "matrix_revision": project.matrix_revision}

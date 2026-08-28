from typing import Literal

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import admin_service

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/admin")
def dashboard(request: Request, days: Literal[1, 7, 30] = 1,
              db: Session = Depends(get_db), user=Depends(admin_service.require_admin)):
    return templates.TemplateResponse(
        request=request, name="admin.html",
        context={"stats": admin_service.statistics(db, days)},
        headers={"Cache-Control": "private, no-store", "X-Robots-Tag": "noindex, nofollow"},
    )

from email_validator import EmailNotValidError, validate_email
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import user_service


router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128


@router.get(
    "/register",
    response_class=HTMLResponse,
)
def registration_form(
    request: Request,
):
    """
    Показывает страницу регистрации.
    """
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "email": "",
            "errors": [],
        },
    )


@router.post(
    "/register",
    response_class=HTMLResponse,
)
def register_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    password_confirmation: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Проверяет форму и создаёт пользователя.
    """
    entered_email = email.strip()
    normalized_email = entered_email
    errors: list[str] = []

    try:
        validated_email = validate_email(
            entered_email,
            check_deliverability=False,
        )

        normalized_email = (
            validated_email.normalized.casefold()
        )
    except EmailNotValidError:
        errors.append(
            "Введите корректный адрес электронной почты."
        )

    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append(
            "Пароль должен содержать не менее "
            f"{MIN_PASSWORD_LENGTH} символов."
        )

    if len(password) > MAX_PASSWORD_LENGTH:
        errors.append(
            "Пароль должен содержать не более "
            f"{MAX_PASSWORD_LENGTH} символов."
        )

    if password != password_confirmation:
        errors.append(
            "Пароль и его подтверждение не совпадают."
        )

    if errors:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "email": entered_email,
                "errors": errors,
            },
            status_code=400,
        )

    user = user_service.create_user(
        db=db,
        email=normalized_email,
        password=password,
    )

    if user is None:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "email": normalized_email,
                "errors": [
                    "Пользователь с таким email уже зарегистрирован."
                ],
            },
            status_code=409,
        )

    return RedirectResponse(
        url="/register/success",
        status_code=303,
    )


@router.get(
    "/register/success",
    response_class=HTMLResponse,
)
def registration_success(
    request: Request,
):
    """
    Показывает подтверждение регистрации.
    """
    return templates.TemplateResponse(
        request=request,
        name="register_success.html",
        context={},
    )
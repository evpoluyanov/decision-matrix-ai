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


def normalize_email_address(
    email: str,
) -> str | None:
    """
    Проверяет и нормализует email.

    Возвращает нормализованный адрес
    или None при некорректном формате.
    """
    try:
        validated_email = validate_email(
            email.strip(),
            check_deliverability=False,
        )
    except EmailNotValidError:
        return None

    return validated_email.normalized.casefold()


@router.get(
    "/register",
    response_class=HTMLResponse,
)
def registration_form(
    request: Request,
):
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
    entered_email = email.strip()
    normalized_email = normalize_email_address(
        entered_email
    )

    errors: list[str] = []

    if normalized_email is None:
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
    return templates.TemplateResponse(
        request=request,
        name="register_success.html",
        context={},
    )


@router.get(
    "/login",
    response_class=HTMLResponse,
)
def login_form(
    request: Request,
):
    if request.session.get("user_id") is not None:
        return RedirectResponse(
            url="/account",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "email": "",
            "error": None,
        },
    )


@router.post(
    "/login",
    response_class=HTMLResponse,
)
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    entered_email = email.strip()

    normalized_email = normalize_email_address(
        entered_email
    )

    user = None

    if normalized_email is not None:
        user = user_service.authenticate_user(
            db=db,
            email=normalized_email,
            password=password,
        )

    if user is None:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "email": entered_email,
                "error": "Неверный email или пароль.",
            },
            status_code=401,
        )

    request.session.clear()

    request.session["user_id"] = user.id

    return RedirectResponse(
        url="/account",
        status_code=303,
    )


@router.get(
    "/account",
    response_class=HTMLResponse,
)
def account(
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = request.session.get("user_id")

    if not isinstance(user_id, int):
        request.session.clear()

        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    user = user_service.get_user_by_id(
        db=db,
        user_id=user_id,
    )

    if user is None:
        request.session.clear()

        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="account.html",
        context={
            "user": user,
        },
    )


@router.post(
    "/logout",
)
def logout_user(
    request: Request,
):
    request.session.clear()

    return RedirectResponse(
        url="/",
        status_code=303,
    )
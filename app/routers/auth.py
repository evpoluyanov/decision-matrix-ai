from email_validator import EmailNotValidError, validate_email
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import (
    email_verification_service,
    user_service,
)

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
    "/verify-email",
    response_class=HTMLResponse,
)
def verify_email_address(
    request: Request,
    token: str = "",
    db: Session = Depends(get_db),
):
    """
    Проверяет ссылку подтверждения
    и обновляет статус пользователя.
    """
    try:
        user_id = (
            email_verification_service
            .verify_email_verification_token(
                token
            )
        )
    except (
        email_verification_service
        .EmailVerificationTokenExpiredError
    ):
        return templates.TemplateResponse(
            request=request,
            name="verify_email.html",
            context={
                "verification_successful": False,
                "result_title": (
                    "Срок действия ссылки истёк"
                ),
                "result_message": (
                    "Эта ссылка подтверждения "
                    "больше не действует."
                ),
            },
            status_code=410,
        )
    except (
        email_verification_service
        .EmailVerificationTokenError
    ):
        return templates.TemplateResponse(
            request=request,
            name="verify_email.html",
            context={
                "verification_successful": False,
                "result_title": (
                    "Ссылка недействительна"
                ),
                "result_message": (
                    "Не удалось проверить "
                    "ссылку подтверждения."
                ),
            },
            status_code=400,
        )

    user = user_service.get_user_by_id(
        db=db,
        user_id=user_id,
    )

    if user is None:
        return templates.TemplateResponse(
            request=request,
            name="verify_email.html",
            context={
                "verification_successful": False,
                "result_title": (
                    "Ссылка недействительна"
                ),
                "result_message": (
                    "Не удалось проверить "
                    "ссылку подтверждения."
                ),
            },
            status_code=400,
        )

    status_changed = (
        user_service.mark_email_as_verified(
            db=db,
            user=user,
        )
    )

    if status_changed:
        result_title = (
            "Email успешно подтверждён"
        )

        result_message = (
            "Теперь вы можете войти "
            "в свою учётную запись."
        )
    else:
        result_title = (
            "Email уже подтверждён"
        )

        result_message = (
            "Этот адрес был подтверждён ранее. "
            "Вы можете войти в систему."
        )

    return templates.TemplateResponse(
        request=request,
        name="verify_email.html",
        context={
            "verification_successful": True,
            "result_title": result_title,
            "result_message": result_message,
        },
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
            "password_errors": [],
            "password_success": False,
        },
    )


@router.post(
    "/account/password",
    response_class=HTMLResponse,
)
def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    new_password_confirmation: str = Form(...),
    db: Session = Depends(get_db),
):
    user_id = request.session.get(
        "user_id"
    )

    if not isinstance(
        user_id,
        int,
    ):
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

    errors = []

    if (
        len(new_password)
        < MIN_PASSWORD_LENGTH
    ):
        errors.append(
            "Новый пароль должен содержать "
            f"не менее {MIN_PASSWORD_LENGTH} символов."
        )

    if (
        len(new_password)
        > MAX_PASSWORD_LENGTH
    ):
        errors.append(
            "Новый пароль должен содержать "
            f"не более {MAX_PASSWORD_LENGTH} символов."
        )

    if (
        new_password
        != new_password_confirmation
    ):
        errors.append(
            "Новый пароль и его подтверждение "
            "не совпадают."
        )

    if errors:
        return templates.TemplateResponse(
            request=request,
            name="account.html",
            context={
                "user": user,
                "password_errors": errors,
                "password_success": False,
            },
            status_code=400,
        )

    changed = (
        user_service.change_password(
            db=db,
            user=user,
            current_password=current_password,
            new_password=new_password,
        )
    )

    if not changed:
        return templates.TemplateResponse(
            request=request,
            name="account.html",
            context={
                "user": user,
                "password_errors": [
                    "Текущий пароль указан неверно."
                ],
                "password_success": False,
            },
            status_code=400,
        )

    return templates.TemplateResponse(
        request=request,
        name="account.html",
        context={
            "user": user,
            "password_errors": [],
            "password_success": True,
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
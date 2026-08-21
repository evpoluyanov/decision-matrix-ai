import logging
from email_validator import EmailNotValidError, validate_email
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import (
    email_service,
    email_verification_service,
    user_service,
)

logger = logging.getLogger(
    __name__
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
    if request.session.get("user_id") is not None:
        return RedirectResponse(
            url="/account",
            status_code=303,
        )

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
    if request.session.get("user_id") is not None:
        return RedirectResponse(
            url="/account",
            status_code=303,
        )

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

    try:
        (
            email_verification_service
            .send_email_verification_message(
                recipient_email=user.email,
                user_id=user.id,
            )
        )
    except (
        email_service.EmailServiceError,
        email_verification_service
        .EmailVerificationError,
    ):
        logger.exception(
            "Не удалось отправить письмо "
            "подтверждения email."
        )

        email_sent = False
    else:
        email_sent = True

    request.session[
        "registration_email_sent"
    ] = email_sent

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
    email_sent = request.session.get(
        "registration_email_sent"
    )

    if email_sent is None:
        return RedirectResponse(
            url="/register",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="register_success.html",
        context={
            "email_sent": email_sent,
        },
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
    Проверяет ссылку, но не подтверждает
    email без действия пользователя.
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
                "confirmation_required": False,
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
                "confirmation_required": False,
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
                "confirmation_required": False,
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

    if user.email_verified:
        return templates.TemplateResponse(
            request=request,
            name="verify_email.html",
            context={
                "confirmation_required": False,
                "verification_successful": True,
                "user_logged_in": (
                    request.session.get(
                        "user_id"
                    )
                    is not None
                ),
                "result_title": (
                    "Email уже подтверждён"
                ),
                "result_message": (
                    "Этот адрес был подтверждён "
                    "ранее. Вы можете войти "
                    "в систему."
                ),
            },
        )

    return templates.TemplateResponse(
        request=request,
        name="verify_email.html",
        context={
            "confirmation_required": True,
            "verification_successful": False,
            "result_title": (
                "Подтвердите email"
            ),
            "result_message": (
                "Нажмите кнопку, чтобы "
                "подтвердить адрес электронной "
                "почты."
            ),
            "token": token,
        },
    )


@router.post(
    "/verify-email",
    response_class=HTMLResponse,
)
def confirm_email_address(
    request: Request,
    token: str = Form(""),
    db: Session = Depends(get_db),
):
    """
    Подтверждает email после явного
    действия пользователя.
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
                "confirmation_required": False,
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
                "confirmation_required": False,
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
                "confirmation_required": False,
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
        verification_result = "confirmed"
    else:
        verification_result = (
            "already_confirmed"
        )

    request.session[
        "email_verification_result"
    ] = verification_result

    return RedirectResponse(
        url="/verify-email/result",
        status_code=303,
    )


@router.get(
    "/verify-email/result",
    response_class=HTMLResponse,
)
def email_verification_result(
    request: Request,
):
    """
    Показывает результат подтверждения
    после перенаправления с POST.
    """
    verification_result = (
        request.session.pop(
            "email_verification_result",
            None,
        )
    )

    if verification_result not in {
        "confirmed",
        "already_confirmed",
    }:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    if verification_result == "confirmed":
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
            "Этот адрес был подтверждён "
            "ранее. Вы можете войти "
            "в систему."
        )

    return templates.TemplateResponse(
        request=request,
        name="verify_email.html",
        context={
            "confirmation_required": False,
            "verification_successful": True,
            "user_logged_in": (
                request.session.get(
                    "user_id"
                )
                is not None
            ),
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
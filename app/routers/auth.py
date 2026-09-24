import logging
from email_validator import EmailNotValidError, validate_email
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth_dependencies import require_user
from app.services import (
    email_service,
    email_verification_service,
    user_service,
    auth_rate_limit_service,
    admin_service,
    attribution_service,
    legal_document_service,
    project_service,
)

logger = logging.getLogger(
    __name__
)

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128


def post_auth_destination(
    db: Session,
    user,
    preferred_project_id=None,
    *,
    welcome: bool = False,
) -> str:
    if isinstance(preferred_project_id, int):
        preferred = project_service.get_project_for_owner(
            db=db,
            project_id=preferred_project_id,
            owner_id=user.id,
        )
        if preferred is not None:
            query = "autofill=1"
            if welcome:
                query += "&welcome=1"
            return f"/projects/{preferred.id}?{query}"
    latest = project_service.get_latest_project(db=db, owner_id=user.id)
    if latest is not None:
        return f"/projects/{latest.id}"
    return "/start"


def limit_form(db, request, action, email, template):
    try:
        auth_rate_limit_service.enforce(db, request, action, email=email)
    except HTTPException as exc:
        return templates.TemplateResponse(
            request=request, name=template,
            context={"email": email, "error": exc.detail, "errors": [exc.detail]},
            status_code=exc.status_code, headers=exc.headers,
        )
    return None


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
    db: Session = Depends(get_db),
):
    if request.session.get("user_id") is not None:
        return RedirectResponse(
            url="/start",
            status_code=303,
        )

    try:
        legal_document_service.registration_versions(db)
    except legal_document_service.LegalDocumentsNotReadyError as exc:
        return templates.TemplateResponse(
            request=request,
            name="registration_unavailable.html",
            context={"message": str(exc)},
            status_code=503,
        )

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "email": "",
            "errors": [],
            "terms_accepted": False,
            "personal_data_consent": False,
            "draft_question": (
                request.session.get("decision_draft", {}).get("question", "")
                if isinstance(request.session.get("decision_draft"), dict)
                else ""
            ),
        },
    )


@router.post(
    "/register",
    response_class=HTMLResponse,
)
def register_user(
    request: Request,
    email: str = Form(..., max_length=320),
    password: str = Form(...),
    password_confirmation: str = Form(...),
    terms_accepted: str | None = Form(None),
    personal_data_consent: str | None = Form(None),
    db: Session = Depends(get_db),
):
    if request.session.get("user_id") is not None:
        return RedirectResponse(
            url="/start",
            status_code=303,
        )

    try:
        legal_versions = legal_document_service.registration_versions(db)
    except legal_document_service.LegalDocumentsNotReadyError as exc:
        return templates.TemplateResponse(
            request=request,
            name="registration_unavailable.html",
            context={"message": str(exc)},
            status_code=503,
        )

    entered_email = email.strip()
    normalized_email = normalize_email_address(
        entered_email
    )

    limited = limit_form(db, request, "register", normalized_email or entered_email, "register.html")
    if limited is not None:
        return limited

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

    if terms_accepted != "yes":
        errors.append(
            "Примите Пользовательское соглашение."
        )

    if personal_data_consent != "yes":
        errors.append(
            "Дайте согласие на обработку персональных данных."
        )

    if errors:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "email": entered_email,
                "errors": errors,
                "terms_accepted": terms_accepted == "yes",
                "personal_data_consent": personal_data_consent == "yes",
            },
            status_code=400,
        )

    user = user_service.create_user(
        db=db,
        email=normalized_email,
        password=password,
        legal_versions=legal_versions,
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
                "terms_accepted": terms_accepted == "yes",
                "personal_data_consent": personal_data_consent == "yes",
            },
            status_code=409,
        )

    attribution_service.link_to_user(
        db=db,
        request=request,
        user=user,
    )

    draft = request.session.get("decision_draft")
    registration_project_id = None
    if isinstance(draft, dict) and str(draft.get("question", "")).strip():
        project = project_service.create_project(
            db=db,
            project_name=str(draft["question"]).strip()[:200],
            project_description=(str(draft.get("details", "")).strip() or None),
            owner_id=user.id,
        )
        registration_project_id = project.id
        request.session.pop("decision_draft", None)

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
    request.session["registration_email"] = user.email
    request.session["registration_user_id"] = user.id
    if registration_project_id is not None:
        request.session["registration_project_id"] = registration_project_id

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
            "registration_email": request.session.get("registration_email", ""),
            "verification_notice": request.session.pop("registration_notice", None),
        },
    )


@router.post("/register/resend-verification")
def resend_registration_verification(
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = request.session.get("registration_user_id")
    user = user_service.get_user_by_id(db=db, user_id=user_id) if isinstance(user_id, int) else None
    if user is None:
        return RedirectResponse("/register", status_code=303)
    if user.email_verified:
        request.session["registration_notice"] = "Email уже подтверждён. Можно войти."
    else:
        auth_rate_limit_service.enforce(db, request, "resend", user_id=user.id)
        try:
            email_verification_service.send_email_verification_message(
                recipient_email=user.email,
                user_id=user.id,
            )
        except (email_service.EmailServiceError, email_verification_service.EmailVerificationError):
            logger.warning("Не удалось повторно отправить подтверждение email.")
            request.session["registration_notice"] = "Не удалось отправить письмо. Попробуйте позже."
        else:
            request.session["registration_notice"] = "Новое письмо отправлено. Проверьте входящие и спам."
            request.session["registration_email_sent"] = True
    return RedirectResponse("/register/success", status_code=303)

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
                "Подтверждаем адрес и открываем "
                "ваше первое решение…"
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

    preferred_project_id = request.session.get("registration_project_id")
    status_changed = (
        user_service.mark_email_as_verified(
            db=db,
            user=user,
        )
    )

    if status_changed:
        destination = post_auth_destination(
            db,
            user,
            preferred_project_id,
            welcome=True,
        )
        request.session.clear()
        request.session["user_id"] = user.id
        if legal_document_service.pending_versions(db, user.id):
            from urllib.parse import quote
            destination = "/legal/updates?next=" + quote(destination, safe="")
        return RedirectResponse(url=destination, status_code=303)

    if request.session.get("user_id") == user.id:
        return RedirectResponse(
            url=post_auth_destination(db, user),
            status_code=303,
        )

    return RedirectResponse(url="/login?verified=1", status_code=303)


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
            url="/start",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "email": "",
            "error": None,
            "draft_question": (
                request.session.get("decision_draft", {}).get("question", "")
                if isinstance(request.session.get("decision_draft"), dict)
                else ""
            ),
        },
    )


@router.post(
    "/login",
    response_class=HTMLResponse,
)
def login_user(
    request: Request,
    email: str = Form(..., max_length=320),
    password: str = Form(..., max_length=MAX_PASSWORD_LENGTH),
    db: Session = Depends(get_db),
):
    entered_email = email.strip()

    normalized_email = normalize_email_address(
        entered_email
    )

    limited = limit_form(db, request, "login", normalized_email or entered_email, "login.html")
    if limited is not None:
        return limited

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
                "draft_question": (
                    request.session.get("decision_draft", {}).get("question", "")
                    if isinstance(request.session.get("decision_draft"), dict)
                    else ""
                ),
            },
            status_code=401,
        )

    draft = request.session.get("decision_draft")
    preferred_project_id = None
    if isinstance(draft, dict) and str(draft.get("question", "")).strip():
        project = project_service.create_project(
            db=db,
            project_name=str(draft["question"]).strip()[:200],
            project_description=(str(draft.get("details", "")).strip() or None),
            owner_id=user.id,
        )
        preferred_project_id = project.id

    request.session.clear()

    request.session["user_id"] = user.id

    destination = post_auth_destination(db, user, preferred_project_id)
    if legal_document_service.pending_versions(db, user.id):
        from urllib.parse import quote
        return RedirectResponse(
            url="/legal/updates?next=" + quote(destination, safe=""),
            status_code=303,
        )

    return RedirectResponse(
        url=destination,
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

    if legal_document_service.pending_versions(db, user.id):
        return RedirectResponse(
            url="/legal/updates?next=%2Faccount",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="account.html",
        context={
            "user": user,
            "password_errors": [],
            "password_success": False,
            "verification_notice": request.session.pop("verification_notice", None),
            "is_admin": admin_service.is_admin(user),
        },
    )


@router.post(
    "/account/password",
    response_class=HTMLResponse,
)
def change_password(
    request: Request,
    current_password: str = Form(..., max_length=MAX_PASSWORD_LENGTH),
    new_password: str = Form(...),
    new_password_confirmation: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(require_user),
):
    auth_rate_limit_service.enforce(db, request, "password", user_id=user.id)
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

@router.post("/account/resend-verification")
def resend_verification(request: Request, db: Session = Depends(get_db),
                        user=Depends(require_user)):
    if user.email_verified:
        request.session["verification_notice"] = "Email уже подтверждён."
    else:
        auth_rate_limit_service.enforce(db, request, "resend", user_id=user.id)
        try:
            email_verification_service.send_email_verification_message(
                recipient_email=user.email, user_id=user.id,
            )
        except (email_service.EmailServiceError, email_verification_service.EmailVerificationError):
            logger.warning("Не удалось повторно отправить подтверждение email.")
            request.session["verification_notice"] = "Не удалось отправить письмо. Попробуйте позже."
        else:
            request.session["verification_notice"] = "Письмо отправлено. Проверьте входящие и спам."
    return RedirectResponse("/account", status_code=303)


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

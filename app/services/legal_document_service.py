"""Versioned legal documents and explicit user confirmations."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from html import escape
import re
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from markupsafe import Markup
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.legal_documents import (
    LEGAL_DOCUMENT_KEYS,
    LEGAL_DOCUMENTS,
    legal_document_definition,
)


MAX_DOCUMENT_LENGTH = 200_000
MAX_SUMMARY_LENGTH = 500
VERSION_PATTERN = re.compile(r"^[0-9A-Za-z][0-9A-Za-z._-]{0,31}$")
MOSCOW = ZoneInfo("Europe/Moscow")


class LegalDocumentError(ValueError):
    pass


class LegalDocumentsNotReadyError(LegalDocumentError):
    pass


class ConfirmationsChangedError(LegalDocumentError):
    pass


def _digest(content: str) -> str:
    return sha256(content.encode("utf-8")).hexdigest()


def _validate_document_values(version: str, content: str, summary: str):
    clean_version = version.strip()
    clean_content = content.strip()
    clean_summary = summary.strip()
    if not VERSION_PATTERN.fullmatch(clean_version):
        raise LegalDocumentError(
            "Версия должна содержать не более 32 латинских букв, цифр, точек, "
            "дефисов или подчёркиваний."
        )
    if not clean_content:
        raise LegalDocumentError("Введите текст документа.")
    if len(clean_content) > MAX_DOCUMENT_LENGTH:
        raise LegalDocumentError("Текст документа превышает 200 000 символов.")
    if len(clean_summary) > MAX_SUMMARY_LENGTH:
        raise LegalDocumentError("Описание изменений превышает 500 символов.")
    return clean_version, clean_content, clean_summary


def current_version(db: Session, document_key: str):
    legal_document_definition(document_key)
    return db.scalar(
        select(models.LegalDocumentVersion)
        .where(
            models.LegalDocumentVersion.document_key == document_key,
            models.LegalDocumentVersion.status == "published",
        )
        .order_by(models.LegalDocumentVersion.published_at.desc())
    )


def version_by_name(db: Session, document_key: str, version: str):
    legal_document_definition(document_key)
    return db.scalar(
        select(models.LegalDocumentVersion).where(
            models.LegalDocumentVersion.document_key == document_key,
            models.LegalDocumentVersion.version == version,
            models.LegalDocumentVersion.status.in_(("published", "archived")),
        )
    )


def latest_draft(db: Session, document_key: str):
    legal_document_definition(document_key)
    return db.scalar(
        select(models.LegalDocumentVersion)
        .where(
            models.LegalDocumentVersion.document_key == document_key,
            models.LegalDocumentVersion.status == "draft",
        )
        .order_by(models.LegalDocumentVersion.created_at.desc())
    )


def version_history(db: Session, document_key: str):
    legal_document_definition(document_key)
    return list(
        db.scalars(
            select(models.LegalDocumentVersion)
            .where(models.LegalDocumentVersion.document_key == document_key)
            .order_by(models.LegalDocumentVersion.created_at.desc())
        )
    )


def suggest_version(db: Session, document_key: str, now: datetime | None = None) -> str:
    legal_document_definition(document_key)
    local_now = (now or datetime.now(timezone.utc)).astimezone(MOSCOW)
    prefix = local_now.date().isoformat()
    existing = set(
        db.scalars(
            select(models.LegalDocumentVersion.version).where(
                models.LegalDocumentVersion.document_key == document_key,
                models.LegalDocumentVersion.version.like(f"{prefix}.%"),
            )
        )
    )
    revision = 1
    while f"{prefix}.{revision}" in existing:
        revision += 1
    return f"{prefix}.{revision}"


def save_draft(
    db: Session,
    *,
    document_key: str,
    version: str,
    content: str,
    change_summary: str,
    admin_user_id: int,
):
    legal_document_definition(document_key)
    clean_version, clean_content, clean_summary = _validate_document_values(
        version, content, change_summary,
    )
    draft = latest_draft(db, document_key)
    if draft is None:
        draft = models.LegalDocumentVersion(
            document_key=document_key,
            version=clean_version,
            content=clean_content,
            change_summary=clean_summary,
            status="draft",
            content_sha256=_digest(clean_content),
            created_by_user_id=admin_user_id,
        )
        db.add(draft)
    else:
        draft.version = clean_version
        draft.content = clean_content
        draft.change_summary = clean_summary
        draft.content_sha256 = _digest(clean_content)
        draft.created_by_user_id = admin_user_id
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise LegalDocumentError("Такая версия документа уже существует.") from exc
    db.refresh(draft)
    return draft


def publish_draft(db: Session, *, document_key: str, draft_id: int, admin_user_id: int):
    legal_document_definition(document_key)
    draft = db.scalar(
        select(models.LegalDocumentVersion)
        .where(
            models.LegalDocumentVersion.id == draft_id,
            models.LegalDocumentVersion.document_key == document_key,
        )
        .with_for_update()
    )
    if draft is None or draft.status != "draft":
        raise LegalDocumentError("Черновик не найден или уже опубликован.")
    _validate_document_values(draft.version, draft.content, draft.change_summary)
    published = list(
        db.scalars(
            select(models.LegalDocumentVersion)
            .where(
                models.LegalDocumentVersion.document_key == document_key,
                models.LegalDocumentVersion.status == "published",
            )
            .with_for_update()
        )
    )
    for previous in published:
        previous.status = "archived"
    draft.status = "published"
    draft.published_at = datetime.now(timezone.utc)
    draft.created_by_user_id = admin_user_id
    draft.content_sha256 = _digest(draft.content)
    db.commit()
    db.refresh(draft)
    return draft


def published_versions(db: Session):
    result = []
    for key in LEGAL_DOCUMENT_KEYS:
        version = current_version(db, key)
        if version is not None:
            result.append(version)
    return result


def registration_versions(db: Session):
    versions = published_versions(db)
    if len(versions) != len(LEGAL_DOCUMENT_KEYS):
        raise LegalDocumentsNotReadyError(
            "Регистрация временно недоступна: юридические документы ещё не опубликованы."
        )
    return versions


def pending_versions(db: Session, user_id: int):
    current = published_versions(db)
    if not current:
        return []
    accepted_ids = set(
        db.scalars(
            select(models.UserLegalAcceptance.document_version_id).where(
                models.UserLegalAcceptance.user_id == user_id,
                models.UserLegalAcceptance.document_version_id.in_(
                    [item.id for item in current]
                ),
            )
        )
    )
    return [item for item in current if item.id not in accepted_ids]


def record_acceptances(db: Session, *, user_id: int, version_ids: list[int]):
    pending = pending_versions(db, user_id)
    if not pending:
        return []
    pending_ids = {item.id for item in pending}
    if set(version_ids) != pending_ids or len(version_ids) != len(pending_ids):
        raise ConfirmationsChangedError(
            "Состав документов изменился. Ознакомьтесь с актуальными редакциями."
        )
    rows = []
    for version in pending:
        definition = LEGAL_DOCUMENTS[version.document_key]
        row = models.UserLegalAcceptance(
            user_id=user_id,
            document_version_id=version.id,
            action=definition.acceptance_action,
        )
        db.add(row)
        rows.append(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        if pending_versions(db, user_id):
            raise
        return []
    return rows


def dashboard_documents(db: Session):
    total_users = db.scalar(select(func.count(models.User.id))) or 0
    rows = []
    for definition in LEGAL_DOCUMENTS.values():
        current = current_version(db, definition.key)
        accepted = 0
        if current is not None:
            accepted = db.scalar(
                select(func.count(models.UserLegalAcceptance.id)).where(
                    models.UserLegalAcceptance.document_version_id == current.id
                )
            ) or 0
        rows.append({
            "definition": definition,
            "current": current,
            "draft": latest_draft(db, definition.key),
            "accepted": accepted,
            "pending": max(total_users - accepted, 0) if current is not None else 0,
        })
    return rows


def safe_next_path(value: str | None) -> str:
    if not value:
        return "/account"
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or not parsed.path.startswith("/"):
        return "/account"
    if parsed.path.startswith("//") or parsed.path == "/legal/updates":
        return "/account"
    result = parsed.path
    if parsed.query:
        result += f"?{parsed.query}"
    return result


def _inline_markup(value: str) -> str:
    def strong(text: str) -> str:
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escape(text))

    parts = []
    position = 0
    for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", value):
        parts.append(strong(value[position:match.start()]))
        label = strong(match.group(1))
        href = match.group(2).strip()
        parsed = urlsplit(href)
        safe = (
            (href.startswith("/") and not href.startswith("//"))
            or parsed.scheme in {"http", "https", "mailto"}
        )
        if safe:
            parts.append(
                f'<a href="{escape(href, quote=True)}">{label}</a>'
            )
        else:
            parts.append(strong(match.group(0)))
        position = match.end()
    parts.append(strong(value[position:]))
    return "".join(parts)


def render_markdown(content: str) -> Markup:
    """Render a deliberately small, HTML-free Markdown subset."""
    blocks: list[str] = []
    paragraph: list[str] = []
    list_kind: str | None = None
    list_items: list[str] = []

    def flush_paragraph():
        if paragraph:
            blocks.append("<p>" + "<br>".join(paragraph) + "</p>")
            paragraph.clear()

    def flush_list():
        nonlocal list_kind
        if list_items and list_kind:
            blocks.append(
                f"<{list_kind}>"
                + "".join(f"<li>{item}</li>" for item in list_items)
                + f"</{list_kind}>"
            )
        list_items.clear()
        list_kind = None

    for raw_line in content.splitlines():
        line = raw_line.strip()
        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        bullet = re.match(r"^[-*]\s+(.+)$", line)
        numbered = re.match(r"^\d+[.)]\s+(.+)$", line)
        if heading:
            flush_paragraph()
            flush_list()
            level = min(len(heading.group(1)) + 1, 5)
            blocks.append(
                f'<h{level} class="mt-4">{_inline_markup(heading.group(2))}</h{level}>'
            )
        elif bullet or numbered:
            flush_paragraph()
            requested_kind = "ul" if bullet else "ol"
            if list_kind and list_kind != requested_kind:
                flush_list()
            list_kind = requested_kind
            list_items.append(_inline_markup((bullet or numbered).group(1)))
        elif not line:
            flush_paragraph()
            flush_list()
        else:
            flush_list()
            paragraph.append(_inline_markup(line))
    flush_paragraph()
    flush_list()
    return Markup("\n".join(blocks))

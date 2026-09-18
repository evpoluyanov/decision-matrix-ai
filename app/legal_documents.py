"""Fixed registry and legacy fallback metadata for legal documents."""

from dataclasses import dataclass


LEGAL_DOCUMENT_DATE = "14.09.2026"
LEGAL_DOCUMENT_VERSION = "2026-09-14"


@dataclass(frozen=True)
class LegalDocumentDefinition:
    key: str
    title: str
    path: str
    acceptance_action: str
    confirmation_label: str


LEGAL_DOCUMENTS = {
    "terms": LegalDocumentDefinition(
        key="terms",
        title="Пользовательское соглашение",
        path="/terms",
        acceptance_action="accepted",
        confirmation_label=(
            "Я ознакомился и принимаю новую редакцию "
            "Пользовательского соглашения."
        ),
    ),
    "privacy": LegalDocumentDefinition(
        key="privacy",
        title="Политика обработки данных пользователей",
        path="/privacy",
        acceptance_action="acknowledged",
        confirmation_label=(
            "Я ознакомился с новой редакцией Политики "
            "обработки данных пользователей."
        ),
    ),
    "consent": LegalDocumentDefinition(
        key="consent",
        title="Согласие на обработку данных пользователя",
        path="/consent",
        acceptance_action="consented",
        confirmation_label=(
            "Я даю согласие на обработку данных на условиях "
            "новой редакции."
        ),
    ),
}

LEGAL_DOCUMENT_KEYS = tuple(LEGAL_DOCUMENTS)


def legal_document_definition(key: str) -> LegalDocumentDefinition:
    try:
        return LEGAL_DOCUMENTS[key]
    except KeyError as exc:
        raise ValueError("Неизвестный юридический документ.") from exc

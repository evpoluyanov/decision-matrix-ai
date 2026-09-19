"""Registry and approved fallback texts for legal documents."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


LEGAL_DOCUMENT_DATE = "19.09.2026"
LEGAL_DOCUMENT_VERSION = "2026-09-19"
LEGAL_CONTENT_DIRECTORY = Path(__file__).with_name("legal_content")


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
        title="Политика в отношении обработки персональных данных",
        path="/privacy",
        acceptance_action="acknowledged",
        confirmation_label=(
            "Я ознакомился с новой редакцией Политики в отношении "
            "обработки персональных данных."
        ),
    ),
    "consent": LegalDocumentDefinition(
        key="consent",
        title="Согласие на обработку персональных данных",
        path="/consent",
        acceptance_action="consented",
        confirmation_label=(
            "Я даю согласие на обработку персональных данных на условиях "
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


@lru_cache(maxsize=len(LEGAL_DOCUMENTS))
def default_legal_document_content(key: str) -> str:
    """Return the reviewed built-in text used for fallback and admin drafts."""
    legal_document_definition(key)
    return (LEGAL_CONTENT_DIRECTORY / f"{key}.md").read_text(
        encoding="utf-8"
    ).strip()

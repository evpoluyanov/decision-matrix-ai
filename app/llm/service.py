import os
from pathlib import Path

from dotenv import load_dotenv

from app.llm.base import LLMProvider
from app.llm.providers.mws import MWSProvider
from app.llm.safety import (
    build_safe_system_prompt,
    validate_prompt_lengths,
)
from app.llm.schemas import LLMResponse


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(
    PROJECT_ROOT / ".env"
)


def get_llm_provider() -> LLMProvider:
    provider_name = os.getenv(
        "LLM_PROVIDER",
        "",
    ).strip().lower()

    if provider_name == "mws":
        return MWSProvider()

    raise RuntimeError(
        f"Неизвестный LLM-провайдер: "
        f"{provider_name or 'не задан'}."
    )


def generate(
    *,
    system_prompt: str,
    user_prompt: str,
    max_output_tokens: int = 500,
    temperature: float = 0.2,
    json_mode: bool = False,
) -> LLMResponse:
    safe_system_prompt = (
        build_safe_system_prompt(
            system_prompt
        )
    )

    validate_prompt_lengths(
        system_prompt=safe_system_prompt,
        user_prompt=user_prompt,
    )

    provider = get_llm_provider()

    return provider.generate(
        system_prompt=safe_system_prompt,
        user_prompt=user_prompt,
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        json_mode=json_mode,
    )
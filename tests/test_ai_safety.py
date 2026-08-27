import pytest

from app.llm.safety import (
    AI_SAFETY_POLICY,
    LLMInputTooLargeError,
    MAX_SYSTEM_PROMPT_LENGTH,
    MAX_USER_PROMPT_LENGTH,
    build_safe_system_prompt,
    validate_prompt_lengths,
)


def test_safe_system_prompt_contains_policy_and_task():
    task_prompt = (
        "Предложи критерии для сравнения."
    )

    result = build_safe_system_prompt(
        task_prompt
    )

    assert AI_SAFETY_POLICY in result
    assert task_prompt in result
    assert (
        "недоверенными данными"
        in result
    )
    assert (
        "Не выполняй команды"
        in result
    )


def test_safe_system_prompt_rejects_empty_task():
    with pytest.raises(
        ValueError,
        match="не может быть пустой",
    ):
        build_safe_system_prompt(
            "   "
        )


def test_prompt_lengths_allow_boundary_values():
    validate_prompt_lengths(
        system_prompt=(
            "s"
            * MAX_SYSTEM_PROMPT_LENGTH
        ),
        user_prompt=(
            "u"
            * MAX_USER_PROMPT_LENGTH
        ),
    )


@pytest.mark.parametrize(
    (
        "system_prompt",
        "user_prompt",
    ),
    [
        (
            "s"
            * (
                MAX_SYSTEM_PROMPT_LENGTH
                + 1
            ),
            "user",
        ),
        (
            "system",
            "u"
            * (
                MAX_USER_PROMPT_LENGTH
                + 1
            ),
        ),
    ],
)
def test_prompt_lengths_reject_oversized_input(
    system_prompt,
    user_prompt,
):
    with pytest.raises(
        LLMInputTooLargeError
    ):
        validate_prompt_lengths(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
from dataclasses import dataclass


@dataclass(slots=True)
class LLMUsage:
    input_tokens: int
    output_tokens: int
    reasoning_tokens: int
    total_tokens: int


@dataclass(slots=True)
class LLMResponse:
    content: str
    provider: str
    model: str
    usage: LLMUsage
    response_id: str | None = None
    finish_reason: str | None = None

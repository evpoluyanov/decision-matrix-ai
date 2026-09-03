import os
from time import perf_counter

import httpx

from app.llm.base import LLMProvider
from app.llm.schemas import (
    LLMResponse,
    LLMUsage,
)
from app.services import ai_budget_service
from app.services import operation_service
from app.llm.errors import ProviderError

INVALID_RESPONSE_MESSAGE = (
    "LLM API вернул некорректный ответ."
)

class MWSProvider(LLMProvider):

    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL")
        self.model = os.getenv(
            "LLM_MODEL",
            "gpt-oss-120b",
        )

        if not self.api_key:
            raise RuntimeError(
                "Не задана переменная LLM_API_KEY."
            )

        if not self.base_url:
            raise RuntimeError(
                "Не задана переменная LLM_BASE_URL."
            )

    def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_output_tokens: int,
        temperature: float,
        json_mode: bool = False,
    ) -> LLMResponse:
        with ai_budget_service.metered_call(
            model=self.model, max_output_tokens=max_output_tokens,
        ) as call:
            started = perf_counter()
            try:
                result = self._generate(
                    system_prompt=system_prompt, user_prompt=user_prompt,
                    max_output_tokens=max_output_tokens, temperature=temperature,
                    json_mode=json_mode, call=call,
                )
            except RuntimeError as exc:
                operation_service.diagnostic(call.request_log_id, "provider", (perf_counter()-started)*1000,
                    code=operation_service.failure_code(exc), http_status=getattr(exc, "http_status", None),
                    finish_reason=getattr(exc, "finish_reason", None), incoming=call.input_tokens, outgoing=call.output_tokens)
                raise
            operation_service.diagnostic(call.request_log_id, "provider", (perf_counter()-started)*1000,
                finish_reason=result.finish_reason, incoming=result.usage.input_tokens, outgoing=result.usage.output_tokens)
            return result

    def _generate(
        self,
        *,
        call,
        system_prompt: str,
        user_prompt: str,
        max_output_tokens: int,
        temperature: float,
        json_mode: bool = False,
    ) -> LLMResponse:

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "max_completion_tokens": (
                max_output_tokens
            ),
            "temperature": temperature,
        }

        if json_mode:
            payload["response_format"] = {
                "type": "json_object",
            }

        http_started = perf_counter()
        try:
            with httpx.Client(
                timeout=45.0,
            ) as client:
                response = client.post(
                    (
                        f"{self.base_url.rstrip('/')}"
                        "/chat/completions"
                    ),
                    headers={
                        "Authorization": (
                            f"Bearer {self.api_key}"
                        ),
                        "Content-Type": (
                            "application/json"
                        ),
                    },
                    json=payload,
                )

                response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise ProviderError(
                "LLM не ответила вовремя.", "provider_timeout"
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise ProviderError(
                "LLM API вернул ошибку.", "provider_http_error", http_status=exc.response.status_code
            ) from exc

        except httpx.RequestError as exc:
            raise ProviderError(
                "Не удалось подключиться к LLM API.", "provider_connection"
            ) from exc

        operation_service.diagnostic(call.request_log_id, "provider_http", (perf_counter()-http_started)*1000, http_status=getattr(response, "status_code", None))
        processing_started = perf_counter()
        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                INVALID_RESPONSE_MESSAGE
            ) from exc

        ai_budget_service.record_usage(call, data)

        if not isinstance(data, dict):
            raise RuntimeError(
                INVALID_RESPONSE_MESSAGE
            )

        choices = data.get(
            "choices"
        )

        if (
            not isinstance(choices, list)
            or not choices
            or not isinstance(
                choices[0],
                dict,
            )
        ):
            raise RuntimeError(
                INVALID_RESPONSE_MESSAGE
            )

        finish_reason = choices[0].get("finish_reason")
        if finish_reason == "length":
            raise ProviderError("Ответ модели обрезан лимитом токенов.", "truncated_response", finish_reason="length")
        message = choices[0].get(
            "message"
        )

        if not isinstance(message, dict):
            raise RuntimeError(
                INVALID_RESPONSE_MESSAGE
            )

        content = message.get(
            "content"
        )

        if (
            not isinstance(content, str)
            or not content.strip()
        ):
            raise RuntimeError(
                INVALID_RESPONSE_MESSAGE
            )

        usage_data = data.get(
            "usage",
            {},
        )

        if not isinstance(
            usage_data,
            dict,
        ):
            raise RuntimeError(
                INVALID_RESPONSE_MESSAGE
            )

        completion_details = usage_data.get(
            "completion_tokens_details",
            {},
        )

        if not isinstance(
            completion_details,
            dict,
        ):
            raise RuntimeError(
                INVALID_RESPONSE_MESSAGE
            )
        usage = LLMUsage(
            input_tokens=usage_data.get(
                "prompt_tokens",
                0,
            ),
            output_tokens=usage_data.get(
                "completion_tokens",
                0,
            ),
            reasoning_tokens=(
                completion_details.get(
                    "reasoning_tokens",
                    0,
                )
            ),
            total_tokens=usage_data.get(
                "total_tokens",
                0,
            ),
        )

        response_id = data.get("id")
        if not isinstance(response_id, str) or not response_id.strip():
            response_id = None
        elif len(response_id) > 200:
            response_id = response_id[:200]

        operation_service.diagnostic(call.request_log_id, "provider_response_processing", (perf_counter()-processing_started)*1000,
            finish_reason=finish_reason, incoming=usage.input_tokens, outgoing=usage.output_tokens)
        return LLMResponse(
            content=content,
            provider="mws",
            model=data.get(
                "model",
                self.model,
            ),
            usage=usage,
            response_id=response_id,
            finish_reason=finish_reason if finish_reason in {"stop", "length", "content_filter"} else None,
        )

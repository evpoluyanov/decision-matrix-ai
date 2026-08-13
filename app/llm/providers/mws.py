import os

import httpx

from app.llm.base import LLMProvider
from app.llm.schemas import (
    LLMResponse,
    LLMUsage,
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
            raise RuntimeError(
                "LLM не ответила вовремя."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                "LLM API вернул ошибку."
            ) from exc

        except httpx.RequestError as exc:
            raise RuntimeError(
                "Не удалось подключиться к LLM API."
            ) from exc

        data = response.json()

        content = (
            data["choices"][0]
            ["message"]["content"]
        )

        usage_data = data.get(
            "usage",
            {},
        )

        completion_details = usage_data.get(
            "completion_tokens_details",
            {},
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

        return LLMResponse(
            content=content,
            provider="mws",
            model=data.get(
                "model",
                self.model,
            ),
            usage=usage,
        )
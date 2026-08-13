from abc import ABC, abstractmethod

from app.llm.schemas import LLMResponse


class LLMProvider(ABC):

    @abstractmethod
    def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_output_tokens: int,
        temperature: float,
        json_mode: bool = False,
    ) -> LLMResponse:
        """
        Отправляет запрос к языковой модели
        и возвращает ответ в едином формате.
        """
        raise NotImplementedError
import argparse
import sys

from dotenv import load_dotenv

from app.services.email_service import (
    EmailServiceError,
    send_email,
)


def parse_arguments() -> argparse.Namespace:
    """
    Получает email и имя получателя
    из команды в терминале.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Отправляет одно тестовое "
            "письмо через Brevo."
        ),
    )

    parser.add_argument(
        "--to",
        required=True,
        help="Email получателя тестового письма.",
    )

    parser.add_argument(
        "--name",
        help="Имя получателя — необязательно.",
    )

    return parser.parse_args()


def main() -> int:
    """
    Загружает настройки и отправляет
    тестовое письмо.
    """
    load_dotenv(
        dotenv_path=".env",
    )

    arguments = parse_arguments()

    try:
        result = send_email(
            recipient_email=arguments.to,
            recipient_name=arguments.name,
            subject=(
                "Тестовое письмо — "
                "Decision Matrix AI"
            ),
            html_content=(
                "<h1>Decision Matrix AI</h1>"
                "<p>Отправка писем через "
                "Brevo работает.</p>"
            ),
            text_content=(
                "Decision Matrix AI\n\n"
                "Отправка писем через "
                "Brevo работает."
            ),
        )
    except (
        EmailServiceError,
        ValueError,
    ) as error:
        print(
            "Не удалось отправить "
            f"тестовое письмо: {error}",
            file=sys.stderr,
        )

        return 1

    print(
        "Тестовое письмо принято "
        "сервисом Brevo."
    )

    if result.message_id:
        print(
            "Идентификатор письма: "
            f"{result.message_id}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
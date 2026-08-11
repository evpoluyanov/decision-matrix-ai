from pwdlib import PasswordHash


# Создаём единый инструмент для хеширования
# и проверки паролей во всём приложении.
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Преобразует обычный пароль в безопасный хеш.

    Исходный пароль после вызова этой функции
    не нужно и нельзя сохранять в базе данных.
    """
    return password_hash.hash(password)


def verify_password(
    password: str,
    stored_password_hash: str,
) -> bool:
    """
    Проверяет, соответствует ли введённый пароль
    хешу, который хранится в базе данных.
    """
    return password_hash.verify(
        password,
        stored_password_hash,
    )
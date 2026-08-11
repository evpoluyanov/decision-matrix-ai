from app.security import hash_password, verify_password


test_password = "ТестовыйПароль-123!"
wrong_password = "НеверныйПароль"

first_hash = hash_password(test_password)
second_hash = hash_password(test_password)

correct_password_is_valid = verify_password(
    test_password,
    first_hash,
)

wrong_password_is_valid = verify_password(
    wrong_password,
    first_hash,
)

print(
    "Используемый алгоритм:",
    first_hash.split("$")[1],
)

print(
    "Хеши одного пароля одинаковые:",
    first_hash == second_hash,
)

print(
    "Правильный пароль принят:",
    correct_password_is_valid,
)

print(
    "Неправильный пароль принят:",
    wrong_password_is_valid,
)


assert first_hash != second_hash
assert correct_password_is_valid is True
assert wrong_password_is_valid is False

print()
print("Механизм хеширования паролей работает корректно.")
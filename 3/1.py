def validate_password(password: str) -> bool:
    if not isinstance(password, str):
        raise TypeError("Пароль должен быть строкой")
    if len(password) < 8:
        return False
    if ' ' in password:
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c.isalpha() for c in password):
        return False
    return True


def divide(a, b):
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Оба аргумента должны быть числами")
    if b == 0:
        raise ZeroDivisionError("Деление на ноль невозможно")
    return a / b

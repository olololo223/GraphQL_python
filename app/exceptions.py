# app/exceptions.py — новый файл
class AppError(Exception):
    """Базовое исключение приложения."""

class EmailAlreadyExistsError(AppError):
    pass

class InvalidCredentialsError(AppError):
    pass
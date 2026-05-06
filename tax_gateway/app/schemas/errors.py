# Унифицированная модель ошибки по ТЗ: {error_code, message, details}.
# Используется для генерации одинаковых ответов при любых сбоях системы.

from typing import Any
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """
    Единый формат ошибок (по ТЗ)
    """
    
    error_code: str
    message: str
    details: dict[str, Any] = {}
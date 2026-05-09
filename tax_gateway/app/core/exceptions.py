from typing import Any, Dict, Optional

class TaxGatewayException(Exception):
    """Базовый класс для всех кастомных ошибок шлюза."""
    def __init__(self, error_code: str, message: str, details: Optional[Dict[str, Any]] = None, status_code: int = 400):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)

class ExternalServiceError(TaxGatewayException):
    """Выбрасывается адаптером, если внешняя налоговая недоступна или вернула ошибку."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code="EXTERNAL_SERVICE_ERROR",
            message=message,
            details=details,
            status_code=502 # Bad Gateway
        )
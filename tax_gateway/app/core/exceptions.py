from typing import Any, Dict, Optional

class TaxGatewayException(RuntimeError):
    """Базовый класс для всех кастомных ошибок шлюза."""
    def __init__(self, error_code: str, message: str, details: Optional[Dict[str, Any]] = None, status_code: int = 400):
        super().__init__(message)

        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.status_code = status_code

class ExternalAdapterError(TaxGatewayException):
    """Выбрасывается адаптером, если внешняя налоговая недоступна или вернула ошибку."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code="EXTERNAL_SERVICE_ERROR",
            message=message,
            details=details,
            status_code=502 # Bad Gateway
        )

class ExternalServiceError(TaxGatewayException):
    def __init__(self, external_adapter_error: ExternalAdapterError):
        super().__init__(
            external_adapter_error.error_code,
            external_adapter_error.message,
            external_adapter_error.details,
            external_adapter_error.status_code
        )


class BadRequestError(TaxGatewayException):
    def __init__(self, message: str, time: float):
        super().__init__(
            error_code="BAD_REQUEST",
            message=message,
            status_code=400
        )
        self.time = time


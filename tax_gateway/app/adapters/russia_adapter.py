import httpx
import logging
import uuid
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from tax_gateway.app.core.exceptions import ExternalAdapterError
from tax_gateway.app.schemas.tax import TaxReportRequest
from tax_gateway.app.services.dto.tax.send_report_result import SendReportResult
from tax_gateway.app.services.dto.tax.get_status_result import GetStatusResult
from tax_gateway.app.services.dto.tax.validate_result import ValidateResult
from tax_gateway.app.services.dto.tax.status import Status

logger = logging.getLogger(__name__)

class RussiaTaxAdapter:
    """
    Адаптер для взаимодействия с налоговой системой РФ (Mock-сервис).
    Реализует TaxAdapterProtocol неявно (duck typing).
    """
    
    def __init__(self) -> None:
        # URL должен выноситься в настройки (config.py)
        self.base_url = "http://localhost:8001/mock-russia" 
    
    def _to_xml(self, request: TaxReportRequest) -> str:
        """Трансформация JSON в XML."""
        xml = f"""
        <TaxReport>
            <IdempotencyKey>{request.idempotency_key}</IdempotencyKey>
            <TaxpayerId>{request.taxpayer_id}</TaxpayerId>
            <Amount>{request.amount}</Amount>
            <Currency>{request.currency}</Currency>
            <Year>{request.year}</Year>
        </TaxReport>
        """
        return xml.strip()

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(httpx.RequestError),
        reraise=True
    )
    async def send_report(self, request: TaxReportRequest) -> SendReportResult:
        """Отправка отчета с логикой повторных попыток при сетевых сбоях."""
        xml_data = self._to_xml(request)
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/submit",
                    content=xml_data,
                    headers={"Content-Type": "application/xml"}
                )
                response.raise_for_status()
                
                return SendReportResult(status=Status.SUCCESS, external_id=uuid.uuid4())
                
            except httpx.HTTPStatusError as e:
                logger.error(f"API РФ вернуло статус ошибки: {e.response.status_code}")
                raise ExternalAdapterError(
                    message="Налоговая РФ отклонила запрос",
                    details={"status_code": e.response.status_code, "response": e.response.text}
                )
            except httpx.RequestError as e:
                logger.error(f"Сетевая ошибка API РФ: {str(e)}")
                raise ExternalAdapterError(
                    message="Налоговая РФ недоступна после серии попыток",
                    details={"error": str(e)}
                )

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(httpx.RequestError),
        reraise=True
    )
    async def get_status(self, report_id: str) -> GetStatusResult:
        """Проверка статуса отчета во внешней налоговой."""

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(f"{self.base_url}/status/{report_id}")
                response.raise_for_status()
                return GetStatusResult(status=Status.SUCCESS, report_id=uuid.UUID(report_id))
            
            except httpx.HTTPStatusError as e:
                logger.error(f"API РФ вернуло статус ошибки при проверке статуса: {e.response.status_code}")
                raise ExternalAdapterError(
                    message="Налоговая РФ отклонила запрос статуса",
                    details={"status_code": e.response.status_code, "response": e.response.text}
                )
            except httpx.RequestError as e:
                logger.error(f"Сетевая ошибка API РФ при проверке статуса: {str(e)}")
                raise ExternalAdapterError(
                    message="Налоговая РФ недоступна при проверке статуса после серии попыток",
                    details={"error": str(e)}
                )

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(httpx.RequestError),
        reraise=True
    )
    async def validate(self, request: TaxReportRequest) -> ValidateResult:
        """Предварительная валидация данных на стороне внешней системы."""

        xml_data = self._to_xml(request)

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/validate",
                    content=xml_data,
                    headers={"Content-Type": "application/xml"}
                )
                response.raise_for_status()
                return ValidateResult(is_valid=True)
            
            except httpx.HTTPStatusError as e:
                logger.error(f"API РФ вернуло статус ошибки при валидации: {e.response.status_code}")
                
                if e.response.status_code == 400:
                    return ValidateResult(is_valid=False)
                
                raise ExternalAdapterError(
                    message="Налоговая РФ отклонила запрос валидации",
                    details={"status_code": e.response.status_code, "response": e.response.text}
                )
            except httpx.RequestError as e:
                logger.error(f"Сетевая ошибка API РФ при валидации: {str(e)}")
                raise ExternalAdapterError(
                    message="Налоговая РФ недоступна при валидации после серии попыток",
                    details={"error": str(e)}
                )


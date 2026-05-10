import abc
import logging
import httpx
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, before_sleep_log
from tax_gateway.app.core.exceptions import ExternalServiceError
from tax_gateway.app.schemas.tax import TaxReportRequest
from tax_gateway.app.services.dto.tax.send_report_result import SendReportResult
from tax_gateway.app.services.dto.tax.get_status_result import GetStatusResult
from tax_gateway.app.services.dto.tax.validate_result import ValidateResult

logger = logging.getLogger(__name__)

class AbstractTaxAdapter(abc.ABC):
    def __init__(self, base_url: str):
        self.base_url = base_url
        self._http_client = httpx.AsyncClient(base_url=self.base_url)

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True,
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def _execute_with_retry(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        response = await self._http_client.request(method, endpoint, **kwargs)
        
        if response.status_code >= 500:
            response.raise_for_status()
            
        return response

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        try:
            response = await self._execute_with_retry(method, endpoint, **kwargs)
            response.raise_for_status()
            
            return response

        except httpx.HTTPError as e:
            if isinstance(e, httpx.HTTPStatusError):
                status_code = e.response.status_code
            else:
                status_code = "СЕТЬ"
            
            raise ExternalServiceError(
                message=f"Ошибка внешней системы. Код: {status_code}",
                details={"error": str(e), "endpoint": endpoint}
            )

    @abc.abstractmethod
    async def send_report(self, request_data: TaxReportRequest) -> SendReportResult:
        pass

    @abc.abstractmethod
    async def get_status(self, report_id: str) -> GetStatusResult:
        pass

    @abc.abstractmethod
    async def validate(self, request_data: TaxReportRequest) -> ValidateResult:
        pass
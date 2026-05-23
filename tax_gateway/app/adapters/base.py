import abc
import logging
import requests
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, before_sleep_log
from tax_gateway.app.core.exceptions import ExternalAdapterError
from tax_gateway.app.schemas.tax import TaxReportRequest
from tax_gateway.app.services.dto.tax.send_report_result import SendReportResult
from tax_gateway.app.services.dto.tax.get_status_result import GetStatusResult
from tax_gateway.app.services.dto.tax.validate_result import ValidateResult

logger = logging.getLogger(__name__)

class AbstractTaxAdapter(abc.ABC):
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._http_client = requests.Session()

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(requests.RequestException),
        reraise=True,
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _execute_with_retry(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        response = self._http_client.request(method, url, **kwargs)
        
        if response.status_code >= 500:
            response.raise_for_status()
            
        return response

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        try:
            response = self._execute_with_retry(method, endpoint, **kwargs)
            response.raise_for_status()
            return response

        except requests.RequestException as e:

            status_code = e.response.status_code if e.response is not None else "СЕТЬ"
            
            raise ExternalAdapterError(
                message=f"Ошибка внешней системы. Код: {status_code}",
                details={"error": str(e), "endpoint": endpoint}
            )

    @abc.abstractmethod
    def send_report(self, request_data: TaxReportRequest) -> SendReportResult:
        pass

    @abc.abstractmethod
    def get_status(self, report_id: str) -> GetStatusResult:
        pass

    @abc.abstractmethod
    def validate(self, request_data: TaxReportRequest) -> ValidateResult:
        pass
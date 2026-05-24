import uuid
import logging

from tax_gateway.app.adapters.base import AbstractTaxAdapter
from tax_gateway.app.schemas.tax import TaxReportRequest
from tax_gateway.app.services.dto.tax.get_status_result import GetStatusResult
from tax_gateway.app.services.dto.tax.send_report_result import SendReportResult
from tax_gateway.app.services.dto.tax.status import Status
from tax_gateway.app.services.dto.tax.validate_result import ValidateResult

logger = logging.getLogger(__name__)

class UsaTaxAdapter(AbstractTaxAdapter):
    """
    Адаптер для налоговой системы США.
    Ожидает JSON API. Демонстрирует маппинг полей под требования внешней системы.
    """

    def __init__(self, base_url: str):
        super().__init__(base_url)
        self._http_client.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def send_report(self, request_data: TaxReportRequest) -> SendReportResult:
        if request_data.currency != "USD":
            return SendReportResult(Status.FAILURE, request_data.idempotency_key)

        usa_payload = {
            "request_id": str(request_data.idempotency_key),
            "ssn": request_data.taxpayer_id,
            "income_usd": float(request_data.amount),
            "tax_year": request_data.year
        }

        response = self._make_request(
            method="POST",
            endpoint="mock-usa/submit",
            json=usa_payload,
            timeout=15
        )

        if response.status_code == 200:
            return SendReportResult(Status.SUCCESS, request_data.idempotency_key)
        
        return SendReportResult(Status.FAILURE, request_data.idempotency_key)

    def get_status(self, report_id: str) -> GetStatusResult:
        response = self._make_request(
            method="GET",
            endpoint=f"mock-usa/status/{report_id}",
            timeout=10
        )
        
        data = response.json()
        
        if data.get("state") == "COMPLETED":
            return GetStatusResult(Status.SUCCESS, uuid.UUID(report_id))
            
        return GetStatusResult(Status.FAILURE, uuid.UUID(report_id))

    def validate(self, request_data: TaxReportRequest) -> ValidateResult:
        usa_payload = {
            "ssn": request_data.taxpayer_id,
            "income_usd": float(request_data.amount),
            "tax_year": request_data.year
        }

        response = self._make_request(
            method="POST",
            endpoint="mock-usa/validate",
            json=usa_payload,
            timeout=10
        )
        
        data = response.json()
        return ValidateResult(is_valid=data.get("valid", False))
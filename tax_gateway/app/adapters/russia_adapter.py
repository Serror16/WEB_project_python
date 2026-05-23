import uuid
from dataclasses import asdict
from tax_gateway.app.adapters.base import AbstractTaxAdapter
from tax_gateway.app.schemas.tax import TaxReportRequest
from tax_gateway.app.services.dto.tax.send_report_result import SendReportResult
from tax_gateway.app.services.dto.tax.get_status_result import GetStatusResult
from tax_gateway.app.services.dto.tax.validate_result import ValidateResult

class RussiaTaxAdapter(AbstractTaxAdapter):
    def __init__(self, base_url: str):
        super().__init__(base_url)
        # Устанавливаем заголовки прямо в сессию
        self._http_client.headers.update({"Content-Type": "application/json"})

    def send_report(self, request_data: TaxReportRequest) -> SendReportResult:
        # Для Pydantic v2
        payload = asdict(request_data)
        
        # Просто вызываем наш умный метод _make_request!
        response = self._make_request("POST", "fns/v1/report", json=payload, timeout=10)
        data = response.json()
        
        return SendReportResult(
            external_id=data.get("external_id"), 
            status=data.get("status")
        )

    def get_status(self, report_id: str) -> GetStatusResult:
        response = self._make_request("GET", f"fns/v1/status/{report_id}", timeout=10)
        data = response.json()
        
        return GetStatusResult(
            report_id=uuid.UUID(report_id),
            status=data.get("status")
        )

    def validate(self, request_data: TaxReportRequest) -> ValidateResult:
        return ValidateResult(is_valid=True)
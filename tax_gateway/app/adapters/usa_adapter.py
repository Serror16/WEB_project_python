import uuid
from tax_gateway.app.adapters.base import AbstractTaxAdapter
from tax_gateway.app.schemas.tax import TaxReportRequest
from tax_gateway.app.services.dto.tax.send_report_result import SendReportResult
from tax_gateway.app.services.dto.tax.get_status_result import GetStatusResult
from tax_gateway.app.services.dto.tax.validate_result import ValidateResult

class UsaTaxAdapter(AbstractTaxAdapter):
    def __init__(self, base_url: str):
        super().__init__(base_url)
        # Специфичные заголовки для IRS (налоговой США)
        self._http_client.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
            # Если потребуется API-ключ, его тоже можно добавить сюда:
            # "Authorization": "Bearer <your_token>"
        })

    def send_report(self, request_data: TaxReportRequest) -> SendReportResult:
        # Конвертируем Pydantic-модель в словарь (для Pydantic v2)
        payload = request_data.model_dump() 
        
        # Вызываем умный метод из базового класса для отправки отчета в IRS
        response = self._make_request("POST", "irs/v1/report", json=payload, timeout=15)
        data = response.json()
        
        return SendReportResult(
            external_id=data.get("external_id"), 
            status=data.get("status")
        )

    def get_status(self, report_id: str) -> GetStatusResult:
        # Получаем статус из специфичного эндпоинта IRS
        response = self._make_request("GET", f"irs/v1/status/{report_id}", timeout=10)
        data = response.json()
        
        return GetStatusResult(
            report_id=uuid.UUID(report_id), 
            status=data.get("status")
        )

    def validate(self, request_data: TaxReportRequest) -> ValidateResult:
        # Здесь в будущем можно добавить специфичную логику проверки для США
        # Например, проверку формата SSN (Social Security Number)
        return ValidateResult(is_valid=True)
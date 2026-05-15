import uuid

from tax_gateway.app.adapters.base import AbstractTaxAdapter
from tax_gateway.app.schemas.tax import TaxReportRequest
from tax_gateway.app.services.dto.tax.get_status_result import GetStatusResult
from tax_gateway.app.services.dto.tax.send_report_result import SendReportResult
from tax_gateway.app.services.dto.tax.status import Status
from tax_gateway.app.services.dto.tax.validate_result import ValidateResult
from tax_gateway.app.utils.xml_parser import dict_to_xml

class UsaTaxAdapter(AbstractTaxAdapter):
    """
    Адаптер для налоговой системы США.
    Ожидает JSON API (согласно мок-серверу на порту 8002).
    Демонстрирует маппинг полей под требования внешней системы.
    """

    def __init__(self):
        super().__init__(base_url="http://127.0.0.1:8002")
    
    async def send_report(self, request_data: TaxReportRequest) -> SendReportResult:
        if request_data.currency != "USD":
            return SendReportResult(Status.FAILURE, request_data.idempotency_key)

        usa_payload = {
                "request_id": str(request_data.idempotency_key),
                "ssn": request_data.taxpayer_id,    # В США это Social Security Number
                "income_usd": float(request_data.amount),  # В США сумма в долларах
                "tax_year": request_data.year
        }


        response = await self._make_request(
            method="POST",
            endpoint="/mock-usa/submit",
            json=usa_payload
        )

        if response.status_code == 200:
            return SendReportResult(Status.SUCCESS, request_data.idempotency_key)
        
        return SendReportResult(Status.FAILURE, request_data.idempotency_key)
    
    async def get_status(self, report_id: str) -> GetStatusResult:
        response = await self._make_request(
            method="GET",
            endpoint=f"/mock-usa/status/{report_id}"
        )
        
        data = response.json()
        
        # Допустим, API США возвращает поле "state" вместо "status", а успех обозначается как "COMPLETED"
        if data.get("state") == "COMPLETED":
            return GetStatusResult(Status.SUCCESS, uuid.UUID(report_id))
            
        return GetStatusResult(Status.FAILURE, uuid.UUID(report_id))
    
    async def validate(self, request_data: TaxReportRequest) -> ValidateResult:
        usa_payload = {
            "ssn": request_data.taxpayer_id,
            "income_usd": float(request_data.amount),
            "tax_year": request_data.year
        }

        response = await self._make_request(
            method="POST",
            endpoint="/mock-usa/validate",
            json=usa_payload
        )
        
        data = response.json()
        # Допустим, API США возвращает булево поле "valid" вместо "is_valid"
        return ValidateResult(is_valid=data.get("valid", False))
import uuid
import logging
from dataclasses import asdict

from tax_gateway.app.adapters.base import AbstractTaxAdapter
from tax_gateway.app.schemas.tax import TaxReportRequest
from tax_gateway.app.services.dto.tax.get_status_result import GetStatusResult
from tax_gateway.app.services.dto.tax.send_report_result import SendReportResult
from tax_gateway.app.services.dto.tax.status import Status
from tax_gateway.app.services.dto.tax.validate_result import ValidateResult
from tax_gateway.app.utils.xml_parser import dict_to_xml

logger = logging.getLogger(__name__)

class RussiaTaxAdapter(AbstractTaxAdapter):
    """
    Адаптер для налоговой системы РФ.
    Ожидает XML API.
    """

    def __init__(self, base_url: str):
        super().__init__(base_url)

    def send_report(self, request_data: TaxReportRequest) -> SendReportResult:
        report_dict = {
            "TaxReport": {
                "IdempotencyKey": str(request_data.idempotency_key),
                "TaxpayerId": request_data.taxpayer_id,
                "Amount": str(request_data.amount),
                "Currency": request_data.currency,
                "Year": str(request_data.year)
            }
        }

        xml_data = dict_to_xml(report_dict)

        response = self._make_request(
            method="POST",
            endpoint="mock-russia/submit",
            data=xml_data,
            headers={"Content-Type": "application/xml"},
            timeout=10
        )

        if response.status_code == 200:
            return SendReportResult(Status.SUCCESS, request_data.idempotency_key)

        return SendReportResult(Status.FAILURE, request_data.idempotency_key)

    def get_status(self, report_id: str) -> GetStatusResult:
        response = self._make_request(
            method="GET",
            endpoint=f"mock-russia/status/{report_id}",
            timeout=10
        )

        data = response.json()

        if data.get("status") == "SUCCESS":
            return GetStatusResult(Status.SUCCESS, uuid.UUID(report_id))

        return GetStatusResult(Status.FAILURE, uuid.UUID(report_id))

    def validate(self, request_data: TaxReportRequest) -> ValidateResult:
        payload = asdict(request_data)
        payload['idempotency_key'] = str(payload['idempotency_key'])
        payload['amount'] = float(payload['amount'])

        response = self._make_request(
            method="POST",
            endpoint="mock-russia/validate",
            json=payload,
            timeout=10
        )

        data = response.json()
        return ValidateResult(is_valid=data.get("is_valid", False))
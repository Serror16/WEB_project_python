from typing import Protocol
from app.schemas.tax import TaxReportRequest
from app.services.dto.tax.send_report_result import SendReportResult
from app.services.dto.tax.get_status_result import GetStatusResult
from app.services.dto.tax.validate_result import ValidateResult

class TaxAdapterProtocol(Protocol):
    """
    Контракт (Protocol) для всех налоговых адаптеров.
    Классам не нужно явно наследоваться от него, достаточно реализовать эти методы.
    """

    async def send_report(self, request: TaxReportRequest) -> SendReportResult:
        ...

    async def get_status(self, report_id: str) -> GetStatusResult:
        ...

    async def validate(self, request: TaxReportRequest) -> ValidateResult:
        ...
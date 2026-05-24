import logging
import time
from typing import Optional

from sqlalchemy.orm import Session

from tax_gateway.app.adapters.base import AbstractTaxAdapter
from tax_gateway.app.core.exceptions import ExternalAdapterError, ExternalServiceError, BadRequestError
from tax_gateway.app.repositories.dto.audit_logs import AuditLogs
from tax_gateway.app.repositories.tax_repository import TaxRepository
from tax_gateway.app.schemas.tax import TaxReportRequest
from tax_gateway.app.services.dto.tax.get_status_result import GetStatusResult
from tax_gateway.app.services.dto.tax.send_report_result import SendReportResult
from tax_gateway.app.services.dto.tax.validate_result import ValidateResult

from tax_gateway.app.adapters.russia_adapter import RussiaTaxAdapter
from tax_gateway.app.adapters.usa_adapter import UsaTaxAdapter

class TaxService:
    __slots__ = ("_tax_repository", "_russia_adapter", "_usa_adapter")

    _logger = logging.getLogger(__name__)

    def __init__(self, database: Session, russia_adapter: RussiaTaxAdapter, usa_adapter: UsaTaxAdapter) -> None:
        self._tax_repository = TaxRepository(database)
        self._russia_adapter = russia_adapter
        self._usa_adapter = usa_adapter

    def send_report(self, tax_report_request: TaxReportRequest) -> SendReportResult:
        self._logger.info(f"TaxService: called send_report; tax_report_request={tax_report_request}")
        
        country: Optional[str] = tax_report_request.country

        if country == "US":
            adapter = self._usa_adapter
        elif country == "RU":
            adapter = self._russia_adapter
        else:
            raise BadRequestError("Unsupported country has been provided", time.perf_counter())

        try:
            start_time: float = time.perf_counter()
            response: SendReportResult = adapter.send_report(tax_report_request)
            end_time: float = time.perf_counter()

            self._tax_repository.save_audit_logs(
                AuditLogs(
                    tax_report_request,
                    {
                        "external_id": str(response.external_id), 
                        "status": response.status.value if hasattr(response.status, 'value') else str(response.status)
                    },
                    start_time,
                    end_time - start_time
                )
            )

            return response
        except ExternalAdapterError as e:
            self._logger.error(e.message)
            raise ExternalServiceError(e)

    def get_status(self, country: str, report_id: str) -> GetStatusResult:
        if country == "US":
            adapter = self._usa_adapter
        elif country == "RU":
            adapter = self._russia_adapter
        else:
            raise BadRequestError("Unsupported country has been provided", time.perf_counter())

        try:
            start_time: float = time.perf_counter()
            response: GetStatusResult = adapter.get_status(report_id)
            end_time: float = time.perf_counter()

            self._tax_repository.save_audit_logs(
                AuditLogs(
                    None,
                    {
                        "country": country, 
                        "report_id": str(response.report_id), 
                        "status": response.status.value if hasattr(response.status, 'value') else str(response.status)
                    },
                    start_time,
                    end_time - start_time,
                    fallback_country=country
                )
            )

            return response
        except ExternalAdapterError as e:
            self._logger.error(e.message)
            raise ExternalServiceError(e)

    def validate(self, tax_report_request: TaxReportRequest) -> ValidateResult:
        self._logger.info(f"TaxService: called validate; tax_report_request={tax_report_request}")
        
        country: Optional[str] = tax_report_request.country

        if country == "US":
            adapter = self._usa_adapter
        elif country == "RU":
            adapter = self._russia_adapter
        else:
            raise BadRequestError("Unsupported country has been provided", time.perf_counter())

        try:
            response: ValidateResult = adapter.validate(tax_report_request)
            return response
        except ExternalAdapterError as e:
            self._logger.error(e.message)
            raise ExternalServiceError(e)
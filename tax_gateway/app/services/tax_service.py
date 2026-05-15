# SPDX-License-Identifier: MIT
"""
Copyright (C) 2026  Andrei Kekishev

This file contains the TaxService, which is the main orchestrator of the system.
"""
import logging
import time
import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from tax_gateway.app.adapters.base import AbstractTaxAdapter
from tax_gateway.app.core.exceptions import ExternalAdapterError, ExternalServiceError, BadRequestError
from tax_gateway.app.repositories.dto.audit_logs import AuditLogs
from tax_gateway.app.repositories.tax_repository import TaxRepository
from tax_gateway.app.schemas.tax import TaxReportRequest
from tax_gateway.app.services.dto.tax.get_status_result import GetStatusResult
from tax_gateway.app.services.dto.tax.send_report_result import SendReportResult
from tax_gateway.app.services.dto.tax.status import Status
from tax_gateway.app.services.dto.tax.validate_result import ValidateResult

from tax_gateway.app.adapters.russia_adapter import RussiaTaxAdapter
from tax_gateway.app.adapters.usa_adapter import UsaTaxAdapter

"""
TaxService handles the following logic:
1. Gets data from API-layer.
2. Chooses the needed adapter by country argument.
3. Saves the audit of requests to the database.
"""


class TaxService:
    __slots__ = ("_tax_repository", "_russia_adapter", "_usa_adapter")

    _logger = logging.getLogger(__name__)

    _tax_repository: TaxRepository
    _russia_adapter: RussiaTaxAdapter
    _usa_adapter: UsaTaxAdapter

    def __init__(self, database: AsyncSession, russia_adapter: RussiaTaxAdapter, usa_adapter: UsaTaxAdapter) -> None:
        self._tax_repository = TaxRepository(database)
        self._russia_adapter = russia_adapter
        self._usa_adapter = usa_adapter

    # Fix needed
    async def send_report(self, tax_report_request: TaxReportRequest) -> SendReportResult:
        self._logger.info("TaxService: called send_report; tax_report_request=" + str(tax_report_request))
        adapter: AbstractTaxAdapter = self._russia_adapter

        country: Optional[str] = tax_report_request.country
        if country is None or country == "":
            # result = defaultAdapter.send_report(tax_report_request)
            return SendReportResult(Status.SUCCESS, uuid.uuid4())

        try:
            match country:
                case "US":
                    adapter = 'us' # fix
                case "RU":
                    adapter = self._russia_adapter
                case _:
                    raise BadRequestError("Unsupported country has been provided", time.perf_counter())

            start_time: float = time.perf_counter()
            response: SendReportResult = await adapter.send_report(tax_report_request)
            end_time: float = time.perf_counter()

            await self._tax_repository.save_audit_logs(
                AuditLogs(
                    tax_report_request,
                    {"external_id": response.external_id, "status": response.status},
                    start_time,
                    end_time - start_time
                )
            )

            return response
        except ExternalAdapterError as e:
            self._logger.error(e.message)
            raise ExternalServiceError(e)

    # Fix needed
    async def get_status(self, country: str, report_id: str) -> GetStatusResult:
        adapter: AbstractTaxAdapter = self._russia_adapter

        start_time: float = time.perf_counter()
        try:
            match country:
                case "US":
                    adapter = 'us'
                    # result = usaAdapter.send_report(tax_report_request)
                case "RU":
                    adapter = self._russia_adapter
                case _:
                    raise BadRequestError("Unsupported country has been provided", time.perf_counter())

            start_time: float = time.perf_counter()
            response: GetStatusResult = await adapter.get_status(report_id)
            end_time: float = time.perf_counter()

            await self._tax_repository.save_audit_logs(
                AuditLogs(
                    None,
                    {"country": country, "report_id": response.report_id, "status": response.status},
                    start_time,
                    end_time - start_time
                )
            )

            return response
        except ExternalAdapterError as e:
            self._logger.error(e.message)
            raise ExternalServiceError(e)

    # Fix needed
    async def validate(self, tax_report_request: TaxReportRequest) -> ValidateResult:
        adapter: AbstractTaxAdapter = self._russia_adapter

        country: Optional[str] = tax_report_request.country
        if country is None or country == "":
            # result = defaultAdapter.send_report(tax_report_request)
            return ValidateResult(True)

        try:
            match country:
                case "US":
                    # adapter = 'us'
                    # result = usaAdapter.send_report(tax_report_request)
                    return ValidateResult(True)
                case "RU":
                    adapter = self._russia_adapter
                case _:
                    raise BadRequestError("Unsupported country has been provided", time.perf_counter())

            start_time: float = time.perf_counter()
            response: ValidateResult = await adapter.validate(tax_report_request)
            end_time: float = time.perf_counter()

            await self._tax_repository.save_audit_logs(
                AuditLogs(
                    tax_report_request,
                    {"is_valid": response.is_valid},
                    start_time,
                    end_time - start_time
                )
            )

            return response
        except ExternalAdapterError as e:
            self._logger.error(e.message)
            raise ExternalServiceError(e)


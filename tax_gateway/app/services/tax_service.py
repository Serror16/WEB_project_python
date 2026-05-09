# SPDX-License-Identifier: MIT
"""
Copyright (C) 2026  Andrei Kekishev

This file contains the TaxService, which is the main orchestrator of the system.
"""
import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from tax_gateway.app.adapters.base import TaxAdapterProtocol
from tax_gateway.app.schemas.tax import TaxReportRequest
from tax_gateway.app.services.dto.tax.get_status_result import GetStatusResult
from tax_gateway.app.services.dto.tax.send_report_result import SendReportResult
from tax_gateway.app.services.dto.tax.status import Status
from tax_gateway.app.services.dto.tax.validate_result import ValidateResult

from tax_gateway.app.adapters.russia_adapter import RussiaTaxAdapter

"""
TaxService handles the following logic:
1. Gets data from API-layer.
2. Chooses the needed adapter by country argument.
3. Saves the audit of requests to the database.
"""

# Add logs
class TaxService:
    __slots__ = ("_database", "_russia_adapter")

    _database: AsyncSession
    _russia_adapter: RussiaTaxAdapter

    def __init__(self, database: AsyncSession, russia_adapter: RussiaTaxAdapter) -> None:
        self._database = database
        self._russia_adapter = russia_adapter

    # Fix needed
    async def send_report(self, tax_report_request: TaxReportRequest) -> SendReportResult:
        adapter: TaxAdapterProtocol = self._russia_adapter

        country: Optional[str] = tax_report_request.country
        if country is None or country == "":
            # result = defaultAdapter.send_report(tax_report_request)
            return SendReportResult(Status.SUCCESS, uuid.uuid4())

        match country:
            case "US":
                # adapter = 'us'
                # result = usaAdapter.send_report(tax_report_request)
                return SendReportResult(Status.SUCCESS, uuid.uuid4())
            case "RU":
                adapter = self._russia_adapter
                return await self._russia_adapter.send_report(tax_report_request)
            case _:
                # result = defaultAdapter.send_report(tax_report_request)
                return SendReportResult(Status.SUCCESS, uuid.uuid4())

    # Fix needed
    async def get_status(self, country: str, report_id: str) -> GetStatusResult:
        adapter: TaxAdapterProtocol = self._russia_adapter

        match country:
            case "US":
                # adapter = 'us'
                # result = usaAdapter.send_report(tax_report_request)
                return GetStatusResult(Status.SUCCESS, uuid.uuid4())
            case "RU":
                adapter = self._russia_adapter
                return await self._russia_adapter.get_status(report_id)
            case _:
                # result = defaultAdapter.send_report(tax_report_request)
                return GetStatusResult(Status.SUCCESS, uuid.uuid4())

    # Fix needed
    async def validate(self, tax_report_request: TaxReportRequest) -> ValidateResult:
        adapter: TaxAdapterProtocol = self._russia_adapter

        country: Optional[str] = tax_report_request.country
        if country is None or country == "":
            # result = defaultAdapter.send_report(tax_report_request)
            return ValidateResult(True)

        match country:
            case "US":
                # adapter = 'us'
                # result = usaAdapter.send_report(tax_report_request)
                return ValidateResult(True)
            case "RU":
                adapter = self._russia_adapter
                return await self._russia_adapter.validate(tax_report_request)
            case _:
                # result = defaultAdapter.send_report(tax_report_request)
                return ValidateResult(True)
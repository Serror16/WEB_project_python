# SPDX-License-Identifier: MIT
"""
Copyright (C) 2026  Andrei Kekishev

This file contains the TaxService, which is the main orchestrator of the system.
"""
import uuid
from typing import Optional

from app.schemas.tax import TaxReportRequest
from app.services.dto.tax.get_status_result import GetStatusResult
from app.services.dto.tax.send_report_result import SendReportResult
from app.services.dto.tax.status import Status
from app.services.dto.tax.validate_result import ValidateResult

from app.adapters.russia_adapter import RussiaTaxAdapter

"""
TaxService handles the following logic:
1. Gets data from API-layer.
2. Chooses the needed adapter by country argument.
3. Realizes retry logic in the case of failure.
4. Saves the audit of requests to the database.
"""


class TaxService:
    __slots__ = ("_russia_adapter",)

    def __init__(self) -> None:
        #self.database = database
        self._russia_adapter = RussiaTaxAdapter()

    # Fix needed
    async def send_report(self, tax_report_request: TaxReportRequest) -> SendReportResult:
        adapter: str = 'default'

        country: Optional[str] = tax_report_request.country
        if country is None or country == "":
            # result = defaultAdapter.send_report(tax_report_request)
            return SendReportResult(Status.SUCCESS, uuid.uuid4())

        match country:
            case "US":
                adapter = 'us'
                # result = usaAdapter.send_report(tax_report_request)
                return SendReportResult(Status.SUCCESS, uuid.uuid4())
            case "RU":
                adapter = 'ru'
                return await self._russia_adapter.send_report(tax_report_request)
            case _:
                # result = defaultAdapter.send_report(tax_report_request)
                return SendReportResult(Status.SUCCESS, uuid.uuid4())

    # Fix needed
    async def get_status(self, country: str, report_id: str) -> GetStatusResult:
        adapter: str = 'default'

        match country:
            case "US":
                adapter = 'us'
                # result = usaAdapter.send_report(tax_report_request)
                return GetStatusResult(Status.SUCCESS, uuid.uuid4())
            case "RU":
                adapter = 'ru'
                return await self._russia_adapter.get_status(report_id)
            case _:
                # result = defaultAdapter.send_report(tax_report_request)
                return GetStatusResult(Status.SUCCESS, uuid.uuid4())

    async def validate(self, tax_report_request: TaxReportRequest) -> ValidateResult:
        adapter: str = 'default'

        country: Optional[str] = tax_report_request.country
        if country is None or country == "":
            # result = defaultAdapter.send_report(tax_report_request)
            return ValidateResult(True)

        match country:
            case "US":
                adapter = 'us'
                # result = usaAdapter.send_report(tax_report_request)
                return ValidateResult(True)
            case "RU":
                adapter = 'ru'
                return await self._russia_adapter.validate(tax_report_request)
            case _:
                # result = defaultAdapter.send_report(tax_report_request)
                return ValidateResult(True)
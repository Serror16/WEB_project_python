# SPDX-License-Identifier: MIT
"""
Copyright (C) 2026  Andrei Kekishev

This file contains the TaxService, which is the main orchestrator of the system.
"""
import uuid
from typing import Optional

from tax_gateway.app.schemas.tax import TaxReportRequest
from tax_gateway.app.services.dto.tax.get_status_result import GetStatusResult
from tax_gateway.app.services.dto.tax.send_report_result import SendReportResult
from tax_gateway.app.services.dto.tax.status import Status
from tax_gateway.app.services.dto.tax.validate_result import ValidateResult

"""
TaxService handles the following logic:
1. Gets data from API-layer.
2. Chooses the needed adapter by country argument.
3. Realizes retry logic in the case of failure.
4. Saves the audit of requests to the database.
"""


class TaxService:
    __slots__ = ()

    def __init__(self) -> None:
        pass

    # Fix needed
    async def send_report(self, tax_report_request: TaxReportRequest) -> SendReportResult:
        adapter: str = 'default'

        try:
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
                    # result = russiaAdapter.send_report(tax_report_request)
                    return SendReportResult(Status.SUCCESS, uuid.uuid4())
                case _:
                    # result = defaultAdapter.send_report(tax_report_request)
                    return SendReportResult(Status.SUCCESS, uuid.uuid4())

        except RuntimeError:
            self._retry_send_report(adapter, tax_report_request, 10)

    # Fix needed
    @staticmethod
    def _retry_send_report(adapter, request: TaxReportRequest, times: int) -> object:
        for _ in range(times):
            try:
                return
            # return adapter.send_report(request)
            except RuntimeError as _:
                pass

    # Fix needed
    async def get_status(self, country: str, report_id: str) -> GetStatusResult:
        adapter: str = 'default'

        try:
            match country:
                case "US":
                    adapter = 'us'
                    # result = usaAdapter.send_report(tax_report_request)
                    return GetStatusResult(Status.SUCCESS, uuid.uuid4())
                case "RU":
                    adapter = 'ru'
                    # result = russiaAdapter.send_report(tax_report_request)
                    return GetStatusResult(Status.SUCCESS, uuid.uuid4())
                case _:
                    # result = defaultAdapter.send_report(tax_report_request)
                    return GetStatusResult(Status.SUCCESS, uuid.uuid4())

        except RuntimeError:
            self._retry_get_status(adapter, report_id, 10)

    # Fix needed
    @staticmethod
    def _retry_get_status(adapter, report_id: str, times: int) -> object:
        for _ in range(times):
            try:
                # return adapter.get_status(report_id)
                return
            except RuntimeError as _:
                pass

    async def validate(self, tax_report_request: TaxReportRequest) -> ValidateResult:
        adapter: str = 'default'

        try:
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
                    # result = russiaAdapter.send_report(tax_report_request)
                    return ValidateResult(True)
                case _:
                    # result = defaultAdapter.send_report(tax_report_request)
                    return ValidateResult(True)

        except RuntimeError:
            self._retry_validate(adapter, tax_report_request, 10)

    @staticmethod
    def _retry_validate(adapter, request: TaxReportRequest, times: int) -> object:
        for _ in range(times):
            try:
                # return adapter.validate(report_id)
                return
            except RuntimeError as _:
                pass
# SPDX-License-Identifier: MIT
"""
Copyright (C) 2026  Andrei Kekishev

This file contains the TaxService, which is the main orchestrator of the system.
"""
import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from tax_gateway.app.adapters.base import AbstractTaxAdapter
from tax_gateway.app.schemas.tax import TaxReportRequest
from tax_gateway.app.services.dto.tax.get_status_result import GetStatusResult
from tax_gateway.app.services.dto.tax.send_report_result import SendReportResult
from tax_gateway.app.services.dto.tax.status import Status
from tax_gateway.app.services.dto.tax.validate_result import ValidateResult

from tax_gateway.app.adapters.russia_adapter import RussiaTaxAdapter
from tax_gateway.app.adapters.usa_adapter import UsaTaxAdapter

class TaxService:
    __slots__ = ("_database", "_russia_adapter", "_usa_adapter")

    _database: AsyncSession
    _russia_adapter: RussiaTaxAdapter
    _usa_adapter: UsaTaxAdapter

    def __init__(self, database: AsyncSession, russia_adapter: RussiaTaxAdapter, usa_adapter: UsaTaxAdapter) -> None:
        self._database = database
        self._russia_adapter = russia_adapter
        self._usa_adapter = usa_adapter

    async def send_report(self, tax_report_request: TaxReportRequest) -> SendReportResult:
        country: Optional[str] = tax_report_request.country
        if country is None or country == "":
            return SendReportResult(Status.SUCCESS, uuid.uuid4())

        match country:
            case "US":
                adapter: AbstractTaxAdapter = self._usa_adapter
            case "RU":
                adapter: AbstractTaxAdapter = self._russia_adapter
            case _:
                return SendReportResult(Status.SUCCESS, uuid.uuid4())

        return await adapter.send_report(tax_report_request)

    async def get_status(self, country: str, report_id: str) -> GetStatusResult:
        match country:
            case "US":
                adapter: AbstractTaxAdapter = self._usa_adapter
            case "RU":
                adapter: AbstractTaxAdapter = self._russia_adapter
            case _:
                return GetStatusResult(Status.SUCCESS, uuid.uuid4())
                
        return await adapter.get_status(report_id)

    async def validate(self, tax_report_request: TaxReportRequest) -> ValidateResult:
        country: Optional[str] = tax_report_request.country
        if country is None or country == "":
            return ValidateResult(True)

        match country:
            case "US":
                adapter: AbstractTaxAdapter = self._usa_adapter
            case "RU":
                adapter: AbstractTaxAdapter = self._russia_adapter
            case _:
                return ValidateResult(True)
                
        return await adapter.validate(tax_report_request)
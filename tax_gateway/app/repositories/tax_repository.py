# SPDX-License-Identifier: MIT
"""
Copyright (C) 2026  Andrei Kekishev
"""
from sqlalchemy.ext.asyncio import AsyncSession

from tax_gateway.app.repositories.dto.audit_logs import AuditLogs


class TaxRepository:
    __slots__ = ("_database",)

    _database: AsyncSession

    def __init__(self, database: AsyncSession) -> None:
        self._database = database

    async def save_audit_logs(self, send_report_audit_logs: AuditLogs) -> None:
        self._database.add(send_report_audit_logs)
        await self._database.commit()
        await self._database.refresh(send_report_audit_logs)


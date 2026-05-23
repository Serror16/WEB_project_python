# SPDX-License-Identifier: MIT
"""
Copyright (C) 2026  Andrei Kekishev
"""
from sqlalchemy.orm import Session

from tax_gateway.app.repositories.dto.audit_logs import AuditLogs
from tax_gateway.app.db.models import AuditLog


class TaxRepository:
    __slots__ = ("_database",)

    _database: Session

    def __init__(self, database: Session) -> None:
        self._database = database

    def save_audit_logs(self, send_report_audit_logs: AuditLogs) -> None:
        db_log = AuditLog(
            idempotency_key=str(send_report_audit_logs.idempotency_key) if send_report_audit_logs.idempotency_key else None,
            user_id=send_report_audit_logs.user_id,
            country=send_report_audit_logs.country,
            request_payload=send_report_audit_logs.request_payload,
            response_payload=send_report_audit_logs.response_payload,
            status_code=send_report_audit_logs.status_code,
            request_creation_time=send_report_audit_logs.request_creation_time,
            request_processing_time=send_report_audit_logs.request_processing_time,
        )
        self._database.add(db_log)
        self._database.commit()
# SPDX-License-Identifier: MIT
"""
Copyright (C) 2026  Andrei Kekishev
"""
import uuid

from tax_gateway.app.services.dto.tax.status import Status


class GetStatusResult:
    __slots__ = ("_report_id", "_status")

    _report_id: uuid.UUID
    _status: Status

    @staticmethod
    def _validate_arguments_for_constructor(status: Status, report_id: uuid.UUID) -> None:
        if not isinstance(status, Status):
            raise TypeError

        if not isinstance(report_id, uuid.UUID):
            raise TypeError

    def __init__(self, status: Status, report_id: uuid.UUID) -> None:
        self._validate_arguments_for_constructor(status, report_id)

        self._status = status
        self._report_id = report_id

    @property
    def status(self) -> Status:
        return self._status

    @property
    def report_id(self) -> uuid.UUID:
        return self._report_id

    @status.getter
    def status(self) -> Status:
        return self._status

    @status.setter
    def status(self, status: Status) -> None:
        if not isinstance(status, Status):
            raise TypeError

        self._status = status

    @report_id.getter
    def report_id(self) -> uuid.UUID:
        return self._report_id

    @report_id.setter
    def report_id(self, report_id: uuid.UUID) -> None:
        if not isinstance(report_id, uuid.UUID):
            raise TypeError

        self._report_id = report_id

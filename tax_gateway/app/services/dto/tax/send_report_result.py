# SPDX-License-Identifier: MIT
"""
Copyright (C) 2026 Kekishev Andrei
"""
import uuid

from tax_gateway.app.services.dto.tax.status import Status


class SendReportResult:
    __slots__ = ("_status", "_external_id")

    _external_id: uuid.UUID
    _status: Status

    @staticmethod
    def _validate_arguments_for_constructor(status: Status, external_id: uuid.UUID) -> None:
        if not isinstance(status, Status):
            raise TypeError

        if not isinstance(external_id, uuid.UUID):
            raise TypeError

    def __init__(self, status: Status, external_id: uuid.UUID) -> None:
        self._validate_arguments_for_constructor(status, external_id)

        self._status = status
        self._external_id = external_id

    @property
    def status(self) -> Status:
        return self._status

    @property
    def external_id(self) -> uuid.UUID:
        return self._external_id

    @status.getter
    def status(self) -> Status:
        return self._status

    @status.setter
    def status(self, status: Status) -> None:
        if not isinstance(status, Status):
            raise TypeError

        self._status = status

    @external_id.getter
    def external_id(self) -> uuid.UUID:
        return self._external_id

    @external_id.setter
    def external_id(self, external_id: uuid.UUID) -> None:
        if not isinstance(external_id, uuid.UUID):
            raise TypeError

        self._external_id = external_id

# SPDX-License-Identifier: MIT
"""
Copyright (C) 2026  Andrei Kekishev
"""
from typing import Any, Optional
import uuid

from pydantic import UUID4

from tax_gateway.app.schemas.tax import TaxReportRequest


class AuditLogs:
    __slots__ = (
        "_idempotency_key",
        "_user_id",
        "_country",
        "_request_payload",
        "_response_payload",
        "_status_code",
        "_request_creation_time",
        "_request_processing_time"
    )

    _idempotency_key: Optional[UUID4]
    _user_id: Optional[str]
    _country: str
    _request_payload: Optional[dict[str, Any]]
    _response_payload: dict[str, Any]
    _status_code: int
    _request_creation_time: float
    _request_processing_time: float

    def __init__(
            self,
            tax_report_request: Optional[TaxReportRequest],
            response_payload: dict[str, Any],
            request_creation_time: float,
            request_processing_time: float,
            fallback_country: str = "UNKNOWN"
    ):

        if tax_report_request is not None:
            self._idempotency_key = tax_report_request.idempotency_key
            self._user_id = tax_report_request.taxpayer_id
            self._country = tax_report_request.country or fallback_country
            self._request_payload = tax_report_request.payload
        else:
            self._idempotency_key = None
            self._user_id = None
            self._country = fallback_country
            self._request_payload = None

        self._response_payload = response_payload
        self._status_code = response_payload.get("status", 500)
        self._request_creation_time = request_creation_time
        self._request_processing_time = request_processing_time

    @property
    def idempotency_key(self) -> Optional[UUID4]:
        return self._idempotency_key

    @idempotency_key.getter
    def idempotency_key(self) -> Optional[UUID4]:
        return self._idempotency_key

    @idempotency_key.setter
    def idempotency_key(self, idempotency_key: Optional[UUID4]) -> None:
        if idempotency_key is not None and not isinstance(idempotency_key, uuid.UUID):
            raise TypeError

        self._idempotency_key = idempotency_key

    @property
    def user_id(self) -> Optional[str]:
        return self._user_id

    @user_id.getter
    def user_id(self) -> Optional[str]:
        return self._user_id

    @user_id.setter
    def user_id(self, user_id: Optional[str]) -> None:
        if user_id is not None and not isinstance(user_id, str):
            raise TypeError

        self._user_id = user_id

    @property
    def country(self) -> str:
        return self._country

    @country.getter
    def country(self) -> str:
        return self._country

    @country.setter
    def country(self, country: str) -> None:
        if not isinstance(country, str):
            raise TypeError

        self._country = country

    @property
    def request_payload(self) -> Optional[dict[str, Any]]:
        return self._request_payload

    @request_payload.getter
    def request_payload(self) -> Optional[dict[str, Any]]:
        return self._request_payload

    @request_payload.setter
    def request_payload(self, request_payload: Optional[dict[str, Any]]) -> None:
        if request_payload is not None and not isinstance(request_payload, dict):
            raise TypeError

        self._request_payload = request_payload

    @property
    def response_payload(self) -> dict[str, Any]:
        return self._response_payload

    @response_payload.getter
    def response_payload(self) -> dict[str, Any]:
        return self._response_payload

    @response_payload.setter
    def response_payload(self, response_payload: dict[str, Any]) -> None:
        if not isinstance(response_payload, dict):
            raise TypeError

        self._response_payload = response_payload

    @property
    def status_code(self) -> int:
        return self._status_code

    @status_code.getter
    def status_code(self) -> int:
        return self._status_code

    @status_code.setter
    def status_code(self, status_code: int) -> None:
        if not isinstance(status_code, int):
            raise TypeError

        self._status_code = status_code

    @property
    def request_creation_time(self) -> float:
        return self._request_creation_time

    @request_creation_time.getter
    def request_creation_time(self) -> float:
        return self._request_creation_time

    @request_creation_time.setter
    def request_creation_time(self, request_creation_time: float) -> None:
        if not isinstance(request_creation_time, float):
            raise TypeError

        self._request_creation_time = request_creation_time

    @property
    def request_processing_time(self) -> float:
        return self._request_processing_time

    @request_processing_time.getter
    def request_processing_time(self) -> float:
        return self._request_processing_time

    @request_processing_time.setter
    def request_processing_time(self, request_processing_time: float) -> None:
        if not isinstance(request_processing_time, float):
            raise TypeError

        self._request_processing_time = request_processing_time
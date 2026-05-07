# SPDX-License-Identifier: MIT
"""
Copyright (C) 2026 Kekishev Andrei
"""

"""
It might be removed if any other field except _is_valid will not be required in API-layer
"""


class ValidateResult:
    __slots__ = ("_is_valid",)

    _is_valid: bool

    @staticmethod
    def _validate_arguments_for_constructor(_is_valid: bool) -> None:
        if not isinstance(_is_valid, bool):
            raise TypeError

    def __init__(self, is_valid: bool) -> None:
        self._validate_arguments_for_constructor(is_valid)

        self._is_valid = is_valid

    @property
    def is_valid(self) -> bool:
        return self._is_valid

    @is_valid.getter
    def is_valid(self) -> bool:
        return self._is_valid

    @is_valid.setter
    def is_valid(self, is_valid: bool) -> None:
        if not isinstance(is_valid, bool):
            raise TypeError

        self._is_valid = is_valid

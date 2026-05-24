
"""
Copyright (C) 2026  Andrei Kekishev
"""

"""
This DTO is supposed to be used in '/register' and '/login' API endpoints.
"""


class AuthenticationResult:
    __slots__ = ("_id", "_email", "_access_token", "_refresh_token")

    _id: str
    _email: str
    _access_token: str
    _refresh_token: str

    @staticmethod
    def _validate_arguments_for_constructor(id: str, email: str, access_token: str, refresh_token: str) -> None:
        if not isinstance(id, str):
            raise TypeError

        if not isinstance(email, str):
            raise TypeError

        if not isinstance(access_token, str):
            raise TypeError

        if not isinstance(refresh_token, str):
            raise TypeError

    def __init__(self, id: str, email: str, access_token: str, refresh_token: str) -> None:
        self._validate_arguments_for_constructor(id, email, access_token, refresh_token)

        self._id = id
        self._email = email
        self._access_token = access_token
        self._refresh_token = refresh_token

    @property
    def id(self) -> str:
        return self._id

    @property
    def email(self) -> str:
        return self._email

    @property
    def access_token(self) -> str:
        return self._access_token

    @property
    def refresh_token(self) -> str:
        return self._refresh_token

    @id.getter
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, id: str) -> None:
        if not isinstance(id, str):
            raise TypeError

        self._id = id

    @email.getter
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, email: str) -> None:
        if not isinstance(email, str):
            raise TypeError

        self._email = email

    @access_token.getter
    def access_token(self) -> str:
        return self._access_token

    @access_token.setter
    def access_token(self, access_token: str) -> None:
        if not isinstance(access_token, str):
            raise TypeError

        self._access_token = access_token

    @refresh_token.getter
    def refresh_token(self) -> str:
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, refresh_token: str) -> None:
        if not isinstance(refresh_token, str):
            raise TypeError

        self._refresh_token = refresh_token


"""
Copyright (C) 2026  Andrei Kekishev
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from tax_gateway.app.db.models import User, BlacklistedToken


class AuthRepository:
    __slots__ = ("_database",)

    _database: Session

    def __init__(self, database: Session) -> None:
        self._database = database

    def find_user_by_email(self, email: str) -> Optional[User]:
        return self._database.execute(select(User).where(User.email == email)).scalar_one_or_none()

    def save_user(self, user: User) -> None:
        self._database.add(user)
        self._database.commit()
        self._database.refresh(user)

    def find_token_by_refresh_token(self, refresh_token: str) -> Optional[BlacklistedToken]:
        return self._database.execute(
            select(BlacklistedToken).where(BlacklistedToken.token == refresh_token)
        ).scalar_one_or_none()

    def save_token(self, token: BlacklistedToken) -> None:
        self._database.add(token)
        self._database.commit()
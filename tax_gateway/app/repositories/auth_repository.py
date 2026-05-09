# SPDX-License-Identifier: MIT
"""
Copyright (C) 2026  Andrei Kekishev
"""
from typing import Any

from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from tax_gateway.app.db.models import User, BlacklistedToken


class AuthRepository:
    __slots__ = ("_database",)

    _database: AsyncSession

    def __init__(self, database: AsyncSession) -> None:
        self._database = database

    async def find_user_by_email(self, email: str) -> Result[tuple[Any]]:
        return await self._database.execute(select(User).where(User.email == email))

    async def save_user(self, user: User) -> None:
        self._database.add(user)
        await self._database.commit()
        await self._database.refresh(user)

    async def find_token_by_refresh_token(self, refresh_token: str) -> Result[tuple[Any]]:
        return await self._database.execute(select(BlacklistedToken).where(BlacklistedToken.token == refresh_token))

    async def save_token(self, token: BlacklistedToken) -> None:
        self._database.add(token)
        await self._database.commit()


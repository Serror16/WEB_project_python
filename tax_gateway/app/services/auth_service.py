# SPDX-License-Identifier: MIT
"""
Copyright (C) 2026  Andrei Kekishev
"""
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from tax_gateway.app.core.security import security_manager
from tax_gateway.app.db.models import User, BlacklistedToken
from tax_gateway.app.repositories.auth_repository import AuthRepository
from tax_gateway.app.schemas.auth import RegisterRequest, LoginRequest, RefreshToAccessRequest, LogoutRequest
from tax_gateway.app.services.dto.auth.authentication_result import AuthenticationResult


class AuthService:
    __slots__ = ("_auth_repository",)

    _auth_repository: AuthRepository

    def __init__(self, database: AsyncSession) -> None:
        self._auth_repository = AuthRepository(database)

    async def register(self, register_request: RegisterRequest) -> AuthenticationResult:
        result = await self._auth_repository.find_user_by_email(register_request.email)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error_code": "EMAIL_EXISTS",
                    "message": "Email уже зарегистрирован",
                    "details": {}
                }
            )

        user: User = User(
            email=register_request.email,
            hashed_password=security_manager.get_hash_password(register_request.password)
        )

        await self._auth_repository.save_user(user)

        access_token = security_manager.create_access_token(data={"email": register_request.email})
        refresh_token = security_manager.create_refresh_token(data={"email": register_request.email})

        return AuthenticationResult(
            user.id,
            user.email,
            access_token,
            refresh_token
        )

    async def login(self, login_request: LoginRequest) -> AuthenticationResult:
        result = await self._auth_repository.find_user_by_email(login_request.email)
        user = result.scalar_one_or_none()

        if not user or not security_manager.check_password(login_request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error_code": "INVALID_CREDENTIALS",
                    "message": "Неверный email или пароль",
                    "details": {}
                }
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error_code": "USER_INACTIVE",
                    "message": "Аккаунт деактивирован",
                    "details": {}
                }
            )

        access = security_manager.create_access_token(data={"email": login_request.email})
        refresh_new = security_manager.create_refresh_token(data={"email": login_request.email})

        return AuthenticationResult(
            user.id,
            user.email,
            access,
            refresh_new
        )

    async def refresh(self, refresh_to_access_request: RefreshToAccessRequest) -> str:
        payload = security_manager.decode_token(refresh_to_access_request.refresh)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": "INVALID_TOKEN", "message": "Неверный тип токена", "details": {}}
            )

        result = await self._auth_repository.find_token_by_refresh_token(refresh_to_access_request.refresh)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error_code": "TOKEN_BLACKLISTED",
                    "message": "Токен уже использован",
                    "details": {}
                }
            )

        email: str = payload.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": "INVALID_TOKEN", "message": "Неверный токен", "details": {}}
            )

        return security_manager.create_access_token(data={"email": email})

    async def logout(self, logout_request: LogoutRequest) -> None:
        try:
            payload = security_manager.decode_token(logout_request.refresh)

            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error_code": "INVALID_TOKEN",
                        "message": "Неверный тип токена",
                        "details": {}
                    }
                )

            blacklisted = BlacklistedToken(
                token=logout_request.refresh,
                expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.UTC)
            )

            await self._auth_repository.save_token(blacklisted)

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "INVALID_TOKEN",
                    "message": "Неверный refresh токен",
                    "details": {}
                }
            )

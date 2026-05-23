# SPDX-License-Identifier: MIT
"""
Copyright (C) 2026  Andrei Kekishev
"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from tax_gateway.app.core.exceptions import (
    TaxGatewayException,
    UnauthorizedException,
    ForbiddenException,
    ConflictException,
)
from tax_gateway.app.core.security import security_manager
from tax_gateway.app.db.models import User, BlacklistedToken
from tax_gateway.app.repositories.auth_repository import AuthRepository
from tax_gateway.app.schemas.auth import RegisterRequest, LoginRequest, RefreshToAccessRequest, LogoutRequest
from tax_gateway.app.services.dto.auth.authentication_result import AuthenticationResult


class AuthService:
    __slots__ = ("_auth_repository",)

    _auth_repository: AuthRepository

    def __init__(self, database: Session) -> None:
        self._auth_repository = AuthRepository(database)

    def register(self, register_request: RegisterRequest) -> AuthenticationResult:
        if self._auth_repository.find_user_by_email(register_request.email):
            raise ConflictException("EMAIL_EXISTS", "Email уже зарегистрирован")

        user = User(
            email=register_request.email,
            hashed_password=security_manager.get_hash_password(register_request.password),
        )
        self._auth_repository.save_user(user)

        access_token = security_manager.create_access_token(data={"email": register_request.email})
        refresh_token = security_manager.create_refresh_token(data={"email": register_request.email})

        return AuthenticationResult(str(user.id), register_request.email, access_token, refresh_token)

    def login(self, login_request: LoginRequest) -> AuthenticationResult:
        user = self._auth_repository.find_user_by_email(login_request.email)

        if not user or not security_manager.check_password(login_request.password, str(user.hashed_password)):
            raise UnauthorizedException("INVALID_CREDENTIALS", "Неверный email или пароль")

        if user.is_active is False:
            raise ForbiddenException("USER_INACTIVE", "Аккаунт деактивирован")

        access = security_manager.create_access_token(data={"email": login_request.email})
        refresh_new = security_manager.create_refresh_token(data={"email": login_request.email})

        return AuthenticationResult(str(user.id), str(user.email), access, refresh_new)

    def refresh(self, refresh_to_access_request: RefreshToAccessRequest) -> str:
        payload = security_manager.decode_token(refresh_to_access_request.refresh)

        if payload.get("type") != "refresh":
            raise UnauthorizedException("INVALID_TOKEN", "Неверный тип токена")

        if self._auth_repository.find_token_by_refresh_token(refresh_to_access_request.refresh):
            raise UnauthorizedException("TOKEN_BLACKLISTED", "Токен уже использован")

        email = payload.get("email")
        if not email:
            raise UnauthorizedException("INVALID_TOKEN", "Неверный токен")

        return security_manager.create_access_token(data={"email": email})

    def logout(self, logout_request: LogoutRequest) -> None:
        try:
            payload = security_manager.decode_token(logout_request.refresh)

            if payload.get("type") != "refresh":
                raise TaxGatewayException("INVALID_TOKEN", "Неверный тип токена", status_code=400)

            blacklisted = BlacklistedToken(
                token=logout_request.refresh,
                expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            )
            self._auth_repository.save_token(blacklisted)

        except TaxGatewayException:
            raise
        except Exception:
            raise TaxGatewayException("INVALID_TOKEN", "Неверный refresh токен", status_code=400)
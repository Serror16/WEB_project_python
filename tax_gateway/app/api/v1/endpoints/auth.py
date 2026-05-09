from fastapi import APIRouter, status

from app.schemas.auth import (
    RegisterRequest, RegisterResponse, LoginRequest, LoginResponse,
    RefreshToAccessRequest, RefreshToAccessResponse, LogoutRequest, LogoutResponse
)
from app.schemas.errors import ErrorResponse
from app.services.auth_service import AuthService
from app.services.dto.auth.authentication_result import AuthenticationResult

auth_service = AuthService()
router = APIRouter(prefix="/auth")


@router.post(
    path="/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 409: {"model": ErrorResponse}}
)
async def register(data: RegisterRequest):
    result: AuthenticationResult = await auth_service.register(data)

    return RegisterResponse(
        id=result.id,
        email=result.email,
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        message="Регистрация: успех"
    )


@router.post(
    path="/login",
    response_model=LoginResponse,
    responses={401: {"model": ErrorResponse}}
)
async def login(data: LoginRequest):
    result: AuthenticationResult = await auth_service.login(data)

    return LoginResponse(
        id=result.id,
        email=result.email,
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        message="Вход: успех"
    )


@router.post(
    path="/refresh",
    response_model=RefreshToAccessResponse,
    responses={401: {"model": ErrorResponse}}
)
async def refresh(data: RefreshToAccessRequest):
    # Test needed. Probable vulnerability here
    token: str = await auth_service.refresh(data)[2]

    return RefreshToAccessResponse(access=token)


@router.post(
    path="/logout",
    response_model=LogoutResponse,
    responses={400: {"model": ErrorResponse}}
)
async def logout(data: LogoutRequest):
    await auth_service.logout(data)

    return LogoutResponse(message="Выход выполнен успешно")

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from tax_gateway.app.db.session import get_db
from tax_gateway.app.schemas.auth import (
    RegisterRequest, RegisterResponse, LoginRequest, LoginResponse,
    RefreshToAccessRequest, RefreshToAccessResponse, LogoutRequest, LogoutResponse
)
from tax_gateway.app.schemas.errors import ErrorResponse
from tax_gateway.app.services.auth_service import AuthService
from tax_gateway.app.services.dto.auth.authentication_result import AuthenticationResult

router = APIRouter(prefix="/auth")

async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)

@router.post(
    path="/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 409: {"model": ErrorResponse}}
)
async def register(data: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)):
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
async def login(data: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
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
async def refresh(data: RefreshToAccessRequest, auth_service: AuthService = Depends(get_auth_service)):
    token: str = await auth_service.refresh(data)

    return RefreshToAccessResponse(access=token)


@router.post(
    path="/logout",
    response_model=LogoutResponse,
    responses={400: {"model": ErrorResponse}}
)
async def logout(data: LogoutRequest, auth_service: AuthService = Depends(get_auth_service)):
    await auth_service.logout(data)

    return LogoutResponse(message="Выход выполнен успешно")

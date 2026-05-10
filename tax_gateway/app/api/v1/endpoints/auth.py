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

router = APIRouter(prefix="/auth", tags=["Authentication"])


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)

@router.post(
    path="/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 409: {"model": ErrorResponse}}
)
async def register(
        request_data: RegisterRequest,
        auth_service: AuthService = Depends(get_auth_service)
):
    """Эндпоинт для регистрации нового пользователя: POST /api/v1/auth/register"""

    result: AuthenticationResult = await auth_service.register(request_data)

    return RegisterResponse(
        id=str(result.id),
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
async def login(
        request_data: LoginRequest,
        auth_service: AuthService = Depends(get_auth_service)
):
    """Эндпоинт для входа в систему: POST /api/v1/auth/login"""

    result: AuthenticationResult = await auth_service.login(request_data)

    return LoginResponse(
        id=str(result.id),
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
async def refresh(
        request_data: RefreshToAccessRequest,
        auth_service: AuthService = Depends(get_auth_service)
):
    """Эндпоинт для обновления access-токена: POST /api/v1/auth/refresh"""

    token: str = await auth_service.refresh(request_data)

    return RefreshToAccessResponse(access=token)


@router.post(
    path="/logout",
    response_model=LogoutResponse,
    responses={400: {"model": ErrorResponse}}
)
async def logout(
        request_data: LogoutRequest,
        auth_service: AuthService = Depends(get_auth_service)
):
    """Эндпоинт для выхода из аккаунта (инвалидация refresh-токена): POST /api/v1/auth/logout"""

    await auth_service.logout(request_data)

    return LogoutResponse(message="Выход выполнен успешно")
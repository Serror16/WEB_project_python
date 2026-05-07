from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from tax_gateway.app.db.session import get_db
from tax_gateway.app.db.models import User, BlacklistedToken
from tax_gateway.app.core.security import security_manager
from tax_gateway.app.schemas.auth import (
    RegisterRequest, RegisterResponse, LoginRequest, LoginResponse,
    RefreshToAccessRequest, RefreshToAccessResponse, LogoutRequest, LogoutResponse
)
from tax_gateway.app.schemas.errors import ErrorResponse


router = APIRouter(prefix="/auth")

@router.post(
    path="/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 409: {"model": ErrorResponse}}
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Регистрация пользователя
    """
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_code": "EMAIL_EXISTS", 
                "message": "Email уже зарегистрирован", 
                "details": {}
            }
        )
    
    user = User(
        email = data.email,
        hashed_password = security_manager.get_hash_password(data.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    access = security_manager.create_access_token(data={"email": data.email})
    refresh_new = security_manager.create_refresh_token(data={"email": data.email})
    
    return RegisterResponse(
        id = user.id,
        email = user.email,
        access_token = access,
        refresh_token = refresh_new,
        message = "Регистрация: успех"
    )

@router.post(
    path="/login",
    response_model=LoginResponse,
    responses={401: {"model": ErrorResponse}}
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Вход в аккаунт
    """
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not security_manager.check_password(data.password, user.hashed_password):
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
    
    access = security_manager.create_access_token(data={"email": data.email})
    refresh_new = security_manager.create_refresh_token(data={"email": data.email})
    
    return LoginResponse(
        id = user.id,
        email = user.email,
        access_token = access,
        refresh_token = refresh_new,
        message = "Вход: успех"
    )

@router.post(
    path="/refresh",
    response_model=RefreshToAccessResponse,
    responses={401: {"model": ErrorResponse}}
)
async def refresh(
    data: RefreshToAccessRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление access токена
    """

    payload = security_manager.decode_token(data.refresh)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "INVALID_TOKEN", "message": "Неверный тип токена", "details": {}}
        )
    
    result = await db.execute(select(BlacklistedToken).where(BlacklistedToken.token == data.refresh))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "TOKEN_BLACKLISTED", 
                "message": "Токен уже использован", 
                "details": {}
            }
        )

    email = payload.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "INVALID_TOKEN", "message": "Неверный токен", "details": {}}
        )

    return RefreshToAccessResponse(access=security_manager.create_access_token(data={"email": email}))


@router.post(
    path="/logout",
    response_model=LogoutResponse,
    responses={400: {"model": ErrorResponse}}
)
async def logout(
    data: LogoutRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Выход из аккаунта
    """

    try:
        payload = security_manager.decode_token(data.refresh)

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
            token=data.refresh,
            expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.UTC)
        )
        db.add(blacklisted)
        await db.commit()
        
        return LogoutResponse(message="Выход выполнен успешно")
        
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
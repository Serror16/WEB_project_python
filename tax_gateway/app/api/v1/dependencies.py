from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import security_manager
from app.db.session import get_db
from app.db.models import User

security = HTTPBearer(auto_error=False)

async def get_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: AsyncSession = Depends(get_db)
) -> User | None:
    """
    Получение текущего пользователя (без обязательной авторизации)
    """

    if not credentials:
        return None
    
    token = credentials.credentials
    payload = security_manager.decode_token(token)

    if payload.get("type") != "access":
        return None
    
    if not payload.get("email"):
        return None
    
    result = await db.execute(select(User).where(User.email == payload.get("email")))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        return None
    
    return user

async def get_current_user_required(
        user: User | None = Depends(get_current_user)
) -> User:
    """
    Получение текущего пользователя (с обязательной авторизацией)
    """

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "UNAUTHORIZED",
                "message": "Требуется авторизация",
                "details": {}
            }
        )
    
    return user


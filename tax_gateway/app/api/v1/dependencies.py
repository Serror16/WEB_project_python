from flask import request, jsonify
from typing import Optional
from functools import wraps
import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from tax_gateway.app.core.exceptions import UnauthorizedException
from tax_gateway.app.core.security import security_manager
from tax_gateway.app.db.models import BlacklistedToken, User
from tax_gateway.app.core.config import Config
from tax_gateway.app.db.session import get_db


def get_current_user(db: Session) -> Optional[User]:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1]
    
    try:
        payload = security_manager.decode_token(token)
    except Exception:
        return None

    if payload.get("type") != "access" or not payload.get("email"):
        return None

    user = db.execute(select(User).where(User.email == payload["email"])).scalar_one_or_none()

    if not user or user.is_active is False:
        return None

    return user


def get_current_user_required(db: Session) -> User:
    user = get_current_user(db)
    if not user:
        raise UnauthorizedException("UNAUTHORIZED", "Требуется авторизация")
    return user


def token_required(f):
    """Декоратор для защиты эндпоинтов"""
    @wraps(f)
    def decorated(*args, **kwargs):
        db = get_db()
        current_user = get_current_user(db)
        
        if not current_user:
            return jsonify({
                "error_code": "UNAUTHORIZED",
                "message": "Неверный, истекший или отсутствующий токен авторизации",
                "details": {}
            }), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def get_refresh_token_user(refresh_token: str) -> Optional[User]:
    """Получение пользователя из refresh токена"""
    try:
        payload = jwt.decode(
            refresh_token,
            Config.SECRET_KEY,
            algorithms=[Config.JWT_ALGORITHM]
        )
        
        if payload.get("type") != "refresh":
            return None
        
        email = payload.get("sub") or payload.get("email")
        if not email:
            return None
        
        db = get_db()
        return db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    except jwt.InvalidTokenError:
        return None


def check_refresh_token_in_blacklist(refresh_token: str) -> bool:
    """Проверка, не в черном ли списке refresh токен"""
    db = get_db()
    token = db.execute(select(BlacklistedToken).where(BlacklistedToken.token == refresh_token)).scalar_one_or_none()
    return token is not None
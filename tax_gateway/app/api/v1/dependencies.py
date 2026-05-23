from flask import request, jsonify
from typing import Optional
from functools import wraps

import jwt

from sqlalchemy import select
from sqlalchemy.orm import Session

from tax_gateway.app.core.exceptions import UnauthorizedException
from tax_gateway.app.core.security import security_manager
from tax_gateway.app.db.models import BlacklistedToken, User
from tax_gateway.app.core.config import settings


def get_current_user(db: Session) -> Optional[User]:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1]
    payload = security_manager.decode_token(token)

    if payload.get("type") != "access" or not payload.get("email"):
        return None

    user = db.execute(select(User).where(User.email == payload["email"])).scalar_one_or_none()

    if not user or not user.is_active:
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
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                "error_code": "MISSING_TOKEN",
                "message": "Отсутствует токен авторизации",
                "details": {}
            }), 401
        
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({
                "error_code": "INVALID_TOKEN_FORMAT",
                "message": "Неверный формат токена. Используйте: Bearer <token>",
                "details": {}
            }), 401
        
        token = parts[1]
        current_user = get_current_user(token)
        
        if not current_user:
            return jsonify({
                "error_code": "INVALID_TOKEN",
                "message": "Неверный или истекший токен",
                "details": {}
            }), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def get_refresh_token_user(refresh_token: str) -> Optional[User]:
    """Получение пользователя из refresh токена"""
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        if payload.get("type") != "refresh":
            return None
        
        email = payload.get("sub")
        if not email:
            return None
        
        return User.query.filter_by(email=email).first()
    except jwt.InvalidTokenError:
        return None


def check_refresh_token_in_blacklist(refresh_token: str) -> bool:
    """Проверка, не в черном ли списке refresh токен"""
    token = BlacklistedToken.query.filter_by(token=refresh_token).first()
    return token is not None
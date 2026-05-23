from functools import wraps
from flask import request, jsonify
import jwt
from typing import Optional

from app.core.config import settings
from app.db.models import User, BlacklistedToken


def get_current_user(token: str) -> Optional[User]:
    """
    Получение пользователя из токена
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        if payload.get("type") != "access":
            return None
        
        email = payload.get("sub")
        if not email:
            return None
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.is_active:
            return None
        
        return user
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """
    Декоратор на проверку токена
    """
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
    """
    Получение пользователя из refresh токена
    """
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
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
    """
    Проверка на черный список refresh токена
    """
    token = BlacklistedToken.query.filter_by(token=refresh_token).first()
    return token is not None
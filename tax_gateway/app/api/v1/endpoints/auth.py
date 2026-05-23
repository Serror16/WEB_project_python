from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from datetime import datetime, timezone
import jwt

from app.core.config import settings
from app.db.session import db_session
from app.db.models import User, BlacklistedToken
from app.api.v1.dependencies import token_required, check_refresh_token_in_blacklist, get_refresh_token_user
from app.schemas.auth import LoginRequestSchema, LogoutRequestSchema, LoginResponseSchema, LogoutResponseSchema, RefreshToAccessRequestSchema, RefreshToAccessResponseSchema
from tax_gateway.app.core.security import create_access_token, create_refresh_token

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Эндпоинт для входа в аккаунт
    ---
    tags:
        - Auth
    parameters:
        - in: body
            name: body
            schema:
            type: object
            required:
                - email
                - password
            properties:
                email:
                type: string
                password:
                type: string
    responses:
        200:
            description: Успешный вход
        401:
            description: Неверные учетные данные
    """
    json_data = request.get_json()
    
    if not json_data:
        return jsonify({
            "error_code": "INVALID_JSON",
            "message": "Тело запроса должно быть валидным JSON",
            "details": {}
        }), 400
    
    # Валидация через Marshmallow
    schema = LoginRequestSchema()
    try:
        data = schema.load(json_data)
    except ValidationError as err:
        return jsonify({
            "error_code": "VALIDATION_ERROR",
            "message": "Ошибка валидации данных",
            "details": err.messages
        }), 422
    
    # Поиск пользователя
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({
            "error_code": "INVALID_CREDENTIALS",
            "message": "Неверный email или пароль",
            "details": {}
        }), 401
    
    if not user.is_active:
        return jsonify({
            "error_code": "USER_INACTIVE",
            "message": "Аккаунт деактивирован",
            "details": {}
        }), 403
    
    # Создание токенов
    access_token = create_access_token(user.email)
    refresh_token = create_refresh_token(user.email)
    
    response_schema = LoginResponseSchema()
    return jsonify(response_schema.dump({
        "id": str(user.id),
        "email": user.email,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "message": "Вход успешен"
    })), 200


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Обновление access токена по refresh"""
    json_data = request.get_json()
    
    if not json_data:
        return jsonify({
            "error_code": "INVALID_JSON",
            "message": "Тело запроса должно быть валидным JSON",
            "details": {}
        }), 400
    
    schema = RefreshToAccessRequestSchema()
    try:
        data = schema.load(json_data)
    except ValidationError as err:
        return jsonify({
            "error_code": "VALIDATION_ERROR",
            "message": "Ошибка валидации данных",
            "details": err.messages
        }), 422
    
    refresh_token = data['refresh']
    
    # Проверка черного списка
    if check_refresh_token_in_blacklist(refresh_token):
        return jsonify({
            "error_code": "TOKEN_BLACKLISTED",
            "message": "Refresh токен уже использован",
            "details": {}
        }), 401
    
    # Получение пользователя из refresh токена
    user = get_refresh_token_user(refresh_token)
    
    if not user:
        return jsonify({
            "error_code": "INVALID_REFRESH_TOKEN",
            "message": "Неверный или истекший refresh токен",
            "details": {}
        }), 401
    
    # Создание нового access токена
    new_access_token = create_access_token(user.email)
    
    response_schema = RefreshToAccessResponseSchema()
    return jsonify(response_schema.dump({
        "access": new_access_token
    })), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Выход (добавление refresh токена в черный список)"""
    json_data = request.get_json()
    
    if not json_data:
        return jsonify({
            "error_code": "INVALID_JSON",
            "message": "Тело запроса должно быть валидным JSON",
            "details": {}
        }), 400
    
    schema = LogoutRequestSchema()
    try:
        data = schema.load(json_data)
    except ValidationError as err:
        return jsonify({
            "error_code": "VALIDATION_ERROR",
            "message": "Ошибка валидации данных",
            "details": err.messages
        }), 422
    
    refresh_token = data['refresh']
    
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        if payload.get("type") != "refresh":
            return jsonify({
                "error_code": "INVALID_TOKEN_TYPE",
                "message": "Неверный тип токена",
                "details": {}
            }), 400
        
        # Добавление в черный список
        blacklisted = BlacklistedToken(
            token=refresh_token,
            expires_at=datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
        )
        db_session.add(blacklisted)
        db_session.commit()
        
        response_schema = LogoutResponseSchema()
        return jsonify(response_schema.dump({
            "message": "Выход выполнен успешно"
        })), 200
        
    except jwt.InvalidTokenError:
        return jsonify({
            "error_code": "INVALID_REFRESH_TOKEN",
            "message": "Неверный refresh токен",
            "details": {}
        }), 400


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Получение информации о текущем пользователе"""
    return jsonify({
        "id": str(current_user.id),
        "email": current_user.email,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat()
    }), 200
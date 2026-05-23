from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from typing import cast
from tax_gateway.app.db.session import get_db
from tax_gateway.app.api.v1.dependencies import token_required
from tax_gateway.app.services.auth_service import AuthService
from tax_gateway.app.schemas.auth import RegisterRequestSchema, RegisterResponseSchema, RegisterRequest

# Импорты схем Marshmallow (валидация JSON) и DTO (передача в сервис)
from tax_gateway.app.schemas.auth import (
    LoginRequestSchema, 
    LogoutRequestSchema, 
    RefreshToAccessRequestSchema,
    LoginResponseSchema, 
    LogoutResponseSchema, 
    RefreshToAccessResponseSchema,
    LoginRequest, 
    LogoutRequest, 
    RefreshToAccessRequest
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    ---
    tags:
      - Auth
    summary: Авторизация пользователя
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - email
              - password
            properties:
              email:
                type: string
                example: "user@example.com"
              password:
                type: string
                example: "strongpassword"
    responses:
      200:
        description: Успешный вход (возвращает токены)
      401:
        description: Неверный email или пароль
    """

    json_data = request.get_json()
    if not json_data:
        return jsonify({"error_code": "INVALID_JSON", "message": "Тело запроса должно быть валидным JSON", "details": {}}), 400
    
    # 1. Валидация Marshmallow
    try:
        data = cast(dict, LoginRequestSchema().load(json_data))
    except ValidationError as err:
        return jsonify({"error_code": "VALIDATION_ERROR", "message": "Ошибка валидации данных", "details": err.messages}), 422
    
    # 2. Сборка DTO и инициализация сервиса
    login_request_dto = LoginRequest(email=data['email'], password=data['password'])
    db = get_db()
    auth_service = AuthService(db)
    
    # 3. Вызов бизнес-логики (ошибки сами улетят в глобальный обработчик __init__.py)
    result = auth_service.login(login_request_dto)
    
    # 4. Формирование ответа
    return jsonify(LoginResponseSchema().dump({
        "id": result.id,
        "email": result.email,
        "access_token": result.access_token,
        "refresh_token": result.refresh_token,
        "message": "Вход успешен"
    })), 200


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """
    ---
    tags:
      - Auth
    summary: Обновление access токена
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - refresh
            properties:
              refresh:
                type: string
                example: "eyJhbGciOiJIUzI1NiIs..."
    responses:
      200:
        description: Новый access токен сгенерирован
      401:
        description: Невалидный или истекший refresh токен
    """

    json_data = request.get_json()
    if not json_data:
        return jsonify({"error_code": "INVALID_JSON", "message": "Тело запроса должно быть JSON", "details": {}}), 400
    
    try:
        data = cast(dict, RefreshToAccessRequestSchema().load(json_data))
    except ValidationError as err:
        return jsonify({"error_code": "VALIDATION_ERROR", "message": "Ошибка валидации данных", "details": err.messages}), 422
    
    refresh_dto = RefreshToAccessRequest(refresh=data['refresh'])
    db = get_db()
    auth_service = AuthService(db)
    
    new_access_token = auth_service.refresh(refresh_dto)
    
    return jsonify(RefreshToAccessResponseSchema().dump({
        "access": new_access_token
    })), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    ---
    tags:
      - Auth
    summary: Выход из системы
    description: Помещает refresh токен в черный список.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - refresh
            properties:
              refresh:
                type: string
                example: "eyJhbGciOiJIUzI1NiIs..."
    responses:
      200:
        description: Успешный выход
      400:
        description: Ошибка при обработке токена
    """
    
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error_code": "INVALID_JSON", "message": "Тело запроса должно быть JSON", "details": {}}), 400
    
    try:
        data = cast(dict, LogoutRequestSchema().load(json_data))
    except ValidationError as err:
        return jsonify({"error_code": "VALIDATION_ERROR", "message": "Ошибка валидации данных", "details": err.messages}), 422
    
    logout_dto = LogoutRequest(refresh=data['refresh'])
    db = get_db()
    auth_service = AuthService(db)
    
    auth_service.logout(logout_dto)
    
    return jsonify(LogoutResponseSchema().dump({
        "message": "Выход выполнен успешно"
    })), 200


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user_info(current_user):
    return jsonify({
        "id": str(current_user.id),
        "email": current_user.email,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }), 200



@auth_bp.route('/register', methods=['POST'])
def register():
    """
    ---
    tags:
      - Auth
    summary: Регистрация нового пользователя
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - email
              - password
            properties:
              email:
                type: string
                example: "user@example.com"
              password:
                type: string
                example: "strongpassword"
    responses:
      201:
        description: Пользователь успешно зарегистрирован
      400:
        description: Ошибка валидации
      409:
        description: Email уже существует
    """

    json_data = request.get_json()
    if not json_data:
        return jsonify({"error_code": "INVALID_JSON", "message": "Тело запроса должно быть валидным JSON", "details": {}}), 400
    
    try:
        data = cast(dict, RegisterRequestSchema().load(json_data))
    except ValidationError as err:
        return jsonify({"error_code": "VALIDATION_ERROR", "message": "Ошибка валидации данных", "details": err.messages}), 422
    
    register_dto = RegisterRequest(email=data['email'], password=data['password'])
    db = get_db()
    auth_service = AuthService(db)
    
    result = auth_service.register(register_dto)
    
    return jsonify(RegisterResponseSchema().dump({
        "id": result.id,
        "email": result.email,
        "access_token": result.access_token,
        "refresh_token": result.refresh_token,
        "message": "Регистрация успешна"
    })), 201
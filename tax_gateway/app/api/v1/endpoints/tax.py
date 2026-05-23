import uuid
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from typing import cast
from tax_gateway.app.core.config import Config
from tax_gateway.app.db.session import get_db
from tax_gateway.app.api.v1.dependencies import token_required

from tax_gateway.app.adapters.russia_adapter import RussiaTaxAdapter
from tax_gateway.app.adapters.usa_adapter import UsaTaxAdapter
from tax_gateway.app.services.tax_service import TaxService

from tax_gateway.app.schemas.tax import (
    TaxReportRequestSchema, 
    TaxReportResponseSchema, 
    TaxStatusResponseSchema,
    TaxReportRequest 
)

tax_bp = Blueprint('tax', __name__)

@tax_bp.route('/report', methods=['POST'])
@token_required
def submit_report(current_user):
    """
    ---
    security:
      - Bearer: []
    tags:
      - Tax
    summary: Отправка налогового отчета
    parameters:
      - in: query
        name: country
        required: true
        schema:
          type: string
          example: "RU"
        description: Код страны (RU или US)
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - taxpayer_id
              - amount
              - currency
              - year
              - idempotency_key
            properties:
              taxpayer_id:
                type: string
                example: "7712345678"
              amount:
                type: number
                example: 150000.50
              currency:
                type: string
                example: "RUB"
              year:
                type: integer
                example: 2023
              idempotency_key:
                type: string
                example: "123e4567-e89b-12d3-a456-426614174000"
              payload:
                type: object
                example: {"document_type": "NDFL-3"}
    responses:
      201:
        description: Отчет успешно отправлен
      400:
        description: Ошибка запроса
      401:
        description: Не авторизован
    """

    country = request.args.get('country')
    if not country:
        return jsonify({"error_code": "MISSING_COUNTRY", "message": "Параметр country обязателен", "details": {}}), 400
    
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error_code": "INVALID_JSON", "message": "Тело запроса должно быть валидным JSON", "details": {}}), 400
    
    # 1. Валидация
    try:
        validated_data = cast(dict, TaxReportRequestSchema().load(json_data))
    except ValidationError as err:
        return jsonify({"error_code": "VALIDATION_ERROR", "message": "Ошибка валидации", "details": err.messages}), 422
    
    # 2. Подготовка DTO
    report_dto = TaxReportRequest(
        taxpayer_id=validated_data["taxpayer_id"],
        amount=validated_data["amount"],
        currency=validated_data["currency"],
        year=validated_data["year"],
        idempotency_key=uuid.UUID(str(validated_data["idempotency_key"])),
        country=country,
        user_id=str(current_user.id)
    )
    
    # 3. Внедрение зависимостей (Dependency Injection) для сервиса
    db = get_db()
    russia_adapter = RussiaTaxAdapter(base_url=Config.RUSSIA_API_URL) 
    usa_adapter = UsaTaxAdapter(base_url=Config.USA_API_URL)
    service = TaxService(db, russia_adapter, usa_adapter)
    
    # 4. Вызов бизнес-логики (замените send_report на то имя метода, которое вы задали в сервисе)
    result = service.send_report(report_dto)
    
    return jsonify(TaxReportResponseSchema().dump({
        "status": result.status,
        "report_id": str(result.external_id),
        "adapter_details": {}
    })), 201


@tax_bp.route('/status/<string:report_id>', methods=['GET'])
@token_required
def check_status(current_user, report_id):
    """
    ---
    security:
      - Bearer: []
    tags:
      - Tax
    summary: Проверка статуса отчета
    parameters:
      - in: path
        name: report_id
        required: true
        schema:
          type: string
          example: "123e4567-e89b-12d3-a456-426614174000"
        description: ID отчета
      - in: query
        name: country
        required: true
        schema:
          type: string
          example: "RU"
        description: Код страны (RU или US)
    responses:
      200:
        description: Текущий статус отчета
      400:
        description: Неверные параметры запроса
      401:
        description: Не авторизован
    """

    country = request.args.get('country', 'russia')
    
    # Собираем сервис со всеми зависимостями
    db = get_db()
    russia_adapter = RussiaTaxAdapter(base_url=Config.RUSSIA_API_URL)
    usa_adapter = UsaTaxAdapter(base_url=Config.USA_API_URL)
    service = TaxService(db, russia_adapter, usa_adapter)
    
    # Вызов логики (замените get_status на то имя метода, которое у вас в сервисе)
    result = service.get_status(
        country=country,
        report_id=report_id
    )
    
    return jsonify(TaxStatusResponseSchema().dump({
        "report_id": str(result.report_id),
        "status": result.status,
        "message": "Success"
    })), 200
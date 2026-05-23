from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app.api.v1.dependencies import token_required
from app.services.tax_service import TaxService
from app.schemas.tax import TaxReportRequestSchema, TaxReportResponseSchema, TaxStatusResponseSchema

tax_bp = Blueprint('tax', __name__, url_prefix='/tax')


@tax_bp.route('/report', methods=['POST'])
@token_required
def submit_report(current_user):
    """
    Эндпоинт для подачи налогового отчета
    ---
    tags:
        - Tax Reports
    parameters:
        - in: query
            name: country
            schema:
                type: string
            required: true
            description: Юрисдикция (страна, например: russia)
    """
    # Получение country из query параметра
    country = request.args.get('country')
    
    if not country:
        return jsonify({
            "error_code": "MISSING_COUNTRY",
            "message": "Параметр country обязателен",
            "details": {}
        }), 400
    
    # Получение JSON тела
    json_data = request.get_json()
    
    if not json_data:
        return jsonify({
            "error_code": "INVALID_JSON",
            "message": "Тело запроса должно быть валидным JSON",
            "details": {}
        }), 400
    
    # Валидация
    schema = TaxReportRequestSchema()
    try:
        validated_data = schema.load(json_data)
    except ValidationError as err:
        return jsonify({
            "error_code": "VALIDATION_ERROR",
            "message": "Ошибка валидации данных",
            "details": err.messages
        }), 422
    
    # Подготовка данных
    report_data = {
        "country": country,
        "idempotency_key": str(validated_data["idempotency_key"]),
        "taxpayer_id": validated_data["taxpayer_id"],
        "amount": str(validated_data["amount"]),  # Decimal в строку
        "currency": validated_data["currency"],
        "year": validated_data["year"],
        "payload": validated_data.get("payload", {})
    }
    
    # Вызов сервиса
    service = TaxService()
    result = service.create_report(
        user_id=current_user.id,
        country=country,
        report_data=report_data,
        idempotency_key=report_data["idempotency_key"]
    )
    
    response_schema = TaxReportResponseSchema()
    return jsonify(response_schema.dump({
        "status": result.get("status", "accepted"),
        "report_id": result.get("report_id"),
        "adapter_details": result.get("adapter_details", {})
    })), 201


@tax_bp.route('/status/<string:report_id>', methods=['GET'])
@token_required
def check_status(current_user, report_id):
    """
    Проверка статуса отчета
    ---
    tags:
        - Tax Reports
    parameters:
        - in: path
            name: report_id
            required: true
            schema:
                type: string
            description: ID отчета
        - in: query
            name: country
            required: false
            schema:
                type: string
                default: russia
            description: Юрисдикция
    """
    country = request.args.get('country', 'russia')
    
    service = TaxService()
    result = service.get_report_status(
        user_id=current_user.id,
        report_id=report_id,
        country=country
    )
    
    if not result:
        return jsonify({
            "error_code": "NOT_FOUND",
            "message": f"Отчет {report_id} не найден",
            "details": {}
        }), 404
    
    response_schema = TaxStatusResponseSchema()
    return jsonify(response_schema.dump({
        "report_id": result.get("report_id"),
        "status": result.get("status"),
        "message": result.get("message"),
        "processed_at": result.get("processed_at")
    })), 200
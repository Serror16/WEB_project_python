from flask import Blueprint, request, jsonify

tax_bp = Blueprint('tax', __name__)

@tax_bp.route('/report', methods=['POST'])
def submit_report():
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
      - in: body
        name: body
        schema:
          type: object
          required:
            - taxpayer_id
            - amount
            - currency
            - year
            - idempotency_key
          properties:
            idempotency_key:
              type: string
              format: uuid
            taxpayer_id:
              type: string
            amount:
              type: number
            currency:
              type: string
            year:
              type: integer
    responses:
      201:
        description: Отчет успешно принят
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: accepted
                report_id:
                  type: string
                  example: 123e4567-e89b-12d3-a456-426614174000
      400:
        description: Ошибка валидации
      502:
        description: Ошибка внешнего сервиса
    """
    # тут должна быть бизнес-логика (потом отредачить!!!)
    # return jsonify({
    #     "status": "accepted",
    #     "report_id": "1234",
    #     "adapter_details": {}
    # }), 201

@tax_bp.route('/status/<string:report_id>', methods=['GET'])
def check_status(report_id):
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
    responses:
      200:
        description: Статус отчета
    """
    # тут должна быть бизнес-логика (потом отредачить!!!)
    # return jsonify({"status": "processing", "report_id": report_id}), 200
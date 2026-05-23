from flask import Flask, jsonify
from flasgger import Swagger
from werkzeug.exceptions import HTTPException
from tax_gateway.app.core.config import Config

def create_app():
    app = Flask(__name__)

    # применение конфига к приложению
    app.config.from_object(Config)

    # настройка Swagger
    app.config['SWAGGER'] = {
        'title': 'Unified Tax API Gateway',
        'uiversion': 3,
        'openapi': '3.0.0'
    }
    swagger = Swagger(app)

    # глобальные обработчики ошибок
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({
            "error_code": "VALIDATION_ERROR",
            "message": "Неверный запрос",
            "details": str(e.description)
        }), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "error_code": "NOT_FOUND",
            "message": "Ресурс не найден",
            "details": {}
        }), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "Внутренняя ошибка сервера",
            "details": {}
        }), 500

    # перехват необработанных исключений
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return e
        return jsonify({
            "error_code": "UNEXPECTED_ERROR",
            "message": str(e),
            "details": {}
        }), 500

    from tax_gateway.app.api.v1.endpoints.tax import tax_bp
    from tax_gateway.app.api.v1.endpoints.auth import auth_bp

    # маршрутизация для апишек
    app.register_blueprint(tax_bp, url_prefix='/api/v1/tax')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')

    return app
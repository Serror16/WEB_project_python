from flask import Flask, jsonify
from flasgger import Swagger
from werkzeug.exceptions import HTTPException

from tax_gateway.app.core.config import Config
from tax_gateway.app.core.exceptions import TaxGatewayException



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "openapi": "3.0.0",
    }

    swagger_template = {
        "openapi": "3.0.0",
        "info": {
            "title": "Unified Tax API Gateway",
            "version": "0.0.1",
        },
        "components": {
            "securitySchemes": {
                "Bearer": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
        },
        "security": [{"Bearer": []}]
    }

    Swagger(app, template=swagger_template, config=swagger_config)

    from tax_gateway.app.db.session import init_db
    db = init_db(app.config['SQLALCHEMY_DATABASE_URI'])

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.remove()

    @app.errorhandler(TaxGatewayException)
    def handle_tax_gateway_exception(e: TaxGatewayException):
        return jsonify({
            "error_code": e.error_code,
            "message": e.message,
            "details": e.details,
        }), e.status_code

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

    app.register_blueprint(tax_bp, url_prefix='/api/v1/tax')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')

    return app
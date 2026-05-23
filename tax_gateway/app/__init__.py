from flask import Flask, jsonify

def create_app():
    app = Flask(__name__)

    # Простой тестовый эндпоинт, чтобы проверить, что всё работает
    @app.route("/ping", methods=["GET"])
    def ping():
        return jsonify({"status": "ok", "framework": "flask"}), 200

    # Здесь позже зарегистрируем наши Блупринты
    # from tax_gateway.app.api.v1.tax import tax_bp
    # app.register_blueprint(tax_bp, url_prefix="/api/v1/tax")

    return app
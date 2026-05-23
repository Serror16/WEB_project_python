from flask import Blueprint
from tax_gateway.app.api.v1.endpoints.auth import auth_bp
from tax_gateway.app.api.v1.endpoints.tax import tax_bp

v1_bp = Blueprint('v1', __name__, url_prefix='/api/v1')

v1_bp.register_blueprint(auth_bp)
v1_bp.register_blueprint(tax_bp)
from flask import Blueprint
from api.v1.endpoints.auth import auth_bp
from api.v1.endpoints.tax import tax_bp

v1_bp = Blueprint('v1', __name__, url_prefix='/api/v1')

v1_bp.register_blueprint(auth_bp)
v1_bp.register_blueprint(tax_bp)
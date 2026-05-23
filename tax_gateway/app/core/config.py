import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Базовые конфигурации Flask-приложения"""

    # настройки бдшки
    raw_db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres"
    )

    # замена +asyncpg из старого .env
    SQLALCHEMY_DATABASE_URI = raw_db_url.replace("+asyncpg", "")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # настройки JWT
    SECRET_KEY = os.getenv("JWT_KEY", "test-key-azaza")  # [cite: 9]
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")  # [cite: 9]
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))  # [cite: 9]
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))  # [cite: 9]

    API_VERSION = os.getenv("API_VERSION", "v1")  # [cite: 9]
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))  # [cite: 9]
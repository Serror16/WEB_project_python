import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Базовые конфигурации Flask-приложения"""


    raw_db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres"
    )

    RUSSIA_API_URL = os.getenv("RUSSIA_API_URL", "http://localhost:8001")
    USA_API_URL = os.getenv("USA_API_URL", "http://localhost:8002")

    SQLALCHEMY_DATABASE_URI = raw_db_url.replace("+asyncpg", "")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    SECRET_KEY = os.getenv("JWT_KEY", "test-key-azaza")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

    API_VERSION = os.getenv("API_VERSION", "v1")
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))

settings = Config()
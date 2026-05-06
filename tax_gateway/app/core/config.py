from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):

    DATABASE_URL = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
        env="DATABASE_URL"
    )

    JWT_KEY = Field(
        default="test-key-azaza", 
        env="JWT_KEY"
    )
    ALGORITHM = Field(
        default="HS256",
        env="JWT_ALGORITHM"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    API_VERSION = "v1"
    REQUEST_TIMEOUT = 30

    class Config:
        env_file = ".env"
        case_sensitive = True
    
settings = Settings()
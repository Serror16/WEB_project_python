from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/postgres",
        validation_alias="DATABASE_URL"
    )

    JWT_KEY: str = Field(
        default="test-key-azaza", 
        validation_alias="JWT_KEY"
    )
    ALGORITHM: str = Field(
        default="HS256",
        validation_alias="JWT_ALGORITHM"
    )
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    API_VERSION: str = "v1"
    REQUEST_TIMEOUT: int = 30

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )
    
settings = Settings()
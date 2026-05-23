from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt  # type: ignore
from passlib.context import CryptContext

from .config import Config
from .exceptions import UnauthorizedException

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


class SecurityManager:

    @staticmethod
    def check_password(password: str, hash_password: str) -> bool:
        return pwd_context.verify(password[:72], hash_password)

    @staticmethod
    def get_hash_password(password: str) -> str:
        return pwd_context.hash(password[:72])

    @staticmethod
    def create_access_token(data: dict[str, Any]) -> str:
        data_copy = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
        data_copy.update({"exp": expire, "type": "access"})
        return jwt.encode(data_copy, Config.SECRET_KEY, algorithm=Config.JWT_ALGORITHM)

    @staticmethod
    def create_refresh_token(data: dict[str, Any]) -> str:
        data_copy = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=Config.REFRESH_TOKEN_EXPIRE_DAYS)
        data_copy.update({"exp": expire, "type": "refresh"})
        return jwt.encode(data_copy, Config.SECRET_KEY, algorithm=Config.JWT_ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        except JWTError as e:
            raise UnauthorizedException(
                "INVALID_TOKEN",
                f"Неверный/истёкший токен: {e}"
            )

    @staticmethod
    def get_email_from_token(token: str) -> str | None:
        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
            return data.get("email")
        except JWTError:
            return None


security_manager = SecurityManager()
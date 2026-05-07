from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt                  #type: ignore
from passlib.context import CryptContext
from fastapi import HTTPException, status
from typing import Any

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityManager:

    @staticmethod
    def check_password(password: str, hash_password: str) -> bool:
        """
        Проверка пароля
        :param password: Строка - пароль
        :param hash_password: Строка - хешированный пароль
        :return: Совпадает или нет
        """
        return pwd_context.verify(password, hash_password)
    
    @staticmethod
    def get_hash_password(password: str) -> str:
        """
        Хеширование пароля
        :param password: Строка - пароль
        :return: Строка - захешированный пароль
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict[str, Any]) -> str:
        """
        Создание access токена
        :param data: Словарь - данные пользователя
        :return: Строка - access токен
        """

        data_copy = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        data_copy.update({"exp": expire, "type": "access"})
        return jwt.encode(data_copy, settings.JWT_KEY, algorithm=settings.ALGORITHM)
    
    @staticmethod
    def create_refresh_token(data: dict[str, Any]) -> str:
        """
        Создание refresh токена
        :param data: Словарь - данные пользователя
        :return: Строка - refresh токен
        """

        data_copy = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        data_copy.update({"exp": expire, "type": "refresh"})
        return jwt.encode(data_copy, settings.JWT_KEY, algorithm=settings.ALGORITHM)
    
    @staticmethod
    def decode_token(token: str) -> dict[str, Any]:
        """
        Декодирование токена
        :param token: Строка - токен
        :return: Словарь - данные пользователя
        """

        try:
            return jwt.decode(token, settings.JWT_KEY, algorithms=[settings.ALGORITHM])
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error_code": "INVALID_TOKEN",
                    "message": "Неверный/истёкший токен",
                    "details": {
                        "error": str(e)
                    }
                }
            )
        
    @staticmethod
    def get_email_from_token(token: str) -> str | None:
        """
        Извлечение email из токена
        :param token: Строка - токен
        :return: Строка - email
        """
        
        try:
            data = jwt.decode(token, settings.JWT_KEY, algorithms=[settings.ALGORITHM])
            return data.get("email")
        except JWTError:
            return None

security_manager = SecurityManager()
from functools import wraps
from flask import request, jsonify
import jwt
from typing import Optional

from flask import request
from sqlalchemy import select
from sqlalchemy.orm import Session

from tax_gateway.app.core.exceptions import UnauthorizedException
from tax_gateway.app.core.security import security_manager
from tax_gateway.app.db.models import User


def get_current_user(db: Session) -> Optional[User]:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1]
    payload = security_manager.decode_token(token)

    if payload.get("type") != "access" or not payload.get("email"):
        return None

    user = db.execute(select(User).where(User.email == payload["email"])).scalar_one_or_none()

    if not user or not user.is_active:
        return None

    return user


def get_current_user_required(db: Session) -> User:
    user = get_current_user(db)
    if not user:
        raise UnauthorizedException("UNAUTHORIZED", "Требуется авторизация")
    return user
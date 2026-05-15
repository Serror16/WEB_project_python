from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, Integer, BigInteger, Float, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


"""
It is necessary for JWT token
"""
class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), unique=True, index=True, nullable=False)
    blacklisted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    idempotency_key = Column(String(50), nullable=True)
    user_id = Column(String(50), nullable=True)
    country = Column(String(10), nullable=False)
    request_payload = Column(JSON, nullable=True)
    response_payload = Column(JSON, nullable=False)
    status_code = Column(Integer, nullable=False)
    request_creation_time = Column(Float, nullable=False)
    request_processing_time = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


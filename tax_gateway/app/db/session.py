from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from tax_gateway.app.db.models import Base

_engine: Optional[Engine] = None
_db_session: Optional[scoped_session] = None


def init_db(database_url: str) -> scoped_session:
    global _engine, _db_session
    _engine = create_engine(database_url, echo=True, pool_pre_ping=True)
    Base.metadata.create_all(bind=_engine)
    _db_session = scoped_session(sessionmaker(bind=_engine, expire_on_commit=False))
    return _db_session


def get_db() -> Session:
    session = _db_session
    assert session is not None, "DB not initialized — call init_db() first"
    return session()


def get_engine():
    return _engine

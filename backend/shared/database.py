"""SQLAlchemy 2.x database helpers.

Each service must set DATABASE_URL to its own schema. This module deliberately
does not define shared ORM models or cross-service foreign keys.
"""
from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from shared.settings import get_settings


class Base(DeclarativeBase):
    """Base class for models owned by a single service."""


def build_engine() -> Engine:
    """Build an engine for this service's configured database."""
    settings = get_settings()
    if not settings.database_url:
        raise RuntimeError(
            "DATABASE_URL is missing. Set it to the service-owned MySQL schema."
        )
    from sqlalchemy import create_engine

    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=1800,
        pool_size=5,
        max_overflow=10,
        future=True,
    )


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Reuse one connection pool per service process."""
    return build_engine()


@lru_cache(maxsize=1)
def get_db_session_factory() -> sessionmaker[Session]:
    """Reuse one session factory per service process."""
    return sessionmaker(
        bind=get_engine(),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields and closes a session per request."""
    db = get_db_session_factory()()
    try:
        yield db
    finally:
        db.close()


def check_database(engine: Engine | None = None) -> bool:
    """Run a lightweight database connectivity check."""
    with (engine or get_engine()).connect() as connection:
        connection.execute(text("SELECT 1"))
    return True

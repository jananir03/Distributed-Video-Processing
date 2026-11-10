from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import get_settings

settings = get_settings()

class Base(DeclarativeBase):
    pass

engine = create_engine(settings.database_url, pool_pre_ping=True, pool_recycle=1800, pool_size=5, max_overflow=5)
worker_engine = create_engine(settings.worker_database_url, pool_pre_ping=True, pool_recycle=1800, pool_size=3, max_overflow=3)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
WorkerSessionLocal = sessionmaker(bind=worker_engine, autoflush=False, autocommit=False, expire_on_commit=False)

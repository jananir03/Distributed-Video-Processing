from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import get_settings

settings = get_settings()
class Base(DeclarativeBase):
    pass

worker_engine = create_engine(settings.database_url, pool_pre_ping=True, pool_recycle=1800)
WorkerSessionLocal = sessionmaker(bind=worker_engine, autoflush=False, autocommit=False, expire_on_commit=False)
orchestrator_engine = create_engine(settings.orchestrator_database_url, pool_pre_ping=True, pool_recycle=1800)
OrchestratorSessionLocal = sessionmaker(bind=orchestrator_engine, autoflush=False, autocommit=False, expire_on_commit=False)

import logging, time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import settings

log = logging.getLogger(__name__)
engine = create_engine(settings.database_url, pool_pre_ping=True, pool_recycle=1800, pool_size=5, max_overflow=10)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

def wait_for_database(attempts=30):
    last = None
    for _ in range(attempts):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except Exception as exc:
            last = exc
            log.warning("Waiting for database: %s", exc)
            time.sleep(2)
    raise RuntimeError("Database unavailable") from last

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

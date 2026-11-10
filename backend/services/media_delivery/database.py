from sqlalchemy import create_engine, text
from .config import get_settings

settings = get_settings()
engine = create_engine(
    settings.worker_database_url,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=5,
    max_overflow=10,
    connect_args={"connect_timeout": 5},
)

def check_database() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

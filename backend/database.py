"""SQLAlchemy engine and session configuration."""
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 加载 backend/.env（确保 DATABASE_URL 等变量在模块导入时就可用）
load_dotenv(Path(__file__).parent / ".env")

# Use env var in Docker, fallback to local path for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mylog.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite needs this for multi-thread
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


def get_db():
    """Dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

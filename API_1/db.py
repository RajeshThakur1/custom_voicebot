"""Database connection and session management - OpenAI Version."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os

# Create data directory if it doesn't exist
os.makedirs("./data", exist_ok=True)

# SQLite database configuration - separate DB for OpenAI version
DATABASE_URL = "sqlite:///./data/OpenAI_RAG.db"

# Create engine with thread safety configuration for SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    from models import Base
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables."""
    from models import Base
    Base.metadata.drop_all(bind=engine)

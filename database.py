from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database configuration
DATABASE_URL = "postgresql+asyncpg://postgres:customerbot@57.159.27.239:5432/customer_support"

# Create SQLAlchemy async engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
engine = create_async_engine(DATABASE_URL)

# Create SessionLocal class
from sqlalchemy.ext.asyncio import async_sessionmaker
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
async def get_db():
    async with SessionLocal() as session:
        yield session
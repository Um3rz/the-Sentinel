"""
Database Configuration

SQLAlchemy async database setup for PostgreSQL (Neon).
Provides engine, session factory, and base class for models.

Input: DATABASE_URL from settings
Output: Async database engine and session management
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Create async engine for PostgreSQL
# NullPool is used to handle serverless connections (like Neon) better
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    poolclass=NullPool,  # Better for serverless databases
    future=True,
)

# Session factory for creating async sessions
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

# Base class for declarative models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database sessions.

    Usage:
        from fastapi import Depends
        from app.core.database import get_db

        @app.get("/items/")
        async def read_items(db: AsyncSession = Depends(get_db)):
            ...

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """
    Create all tables defined in models.
    Should be called on application startup.

    Note: In production, use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """
    Drop all tables. Use with caution!
    Mainly for testing purposes.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

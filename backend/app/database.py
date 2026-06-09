import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.config import settings

logger = logging.getLogger(__name__)

# Base class for SQLAlchemy ORM models
Base = declarative_base()

# Async PostgreSQL Connection Engine
# Production-ready pooling setup:
# - pool_size: number of connections kept persistently in the pool
# - max_overflow: extra connections that can be opened beyond pool_size
# - pool_pre_ping: test connection health before yielding to queries (prevents stale DB sockets)
# - pool_recycle: cycle connections periodically (e.g. 1 hour) to clear DB leaks
# Determine if connecting to a remote host (e.g. Neon, Supabase) and configure SSL accordingly
connect_args = {}
if "localhost" not in settings.DATABASE_URL and "127.0.0.1" not in settings.DATABASE_URL and "postgres" not in settings.DATABASE_URL:
    connect_args["ssl"] = True

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,  # Set to True to print all SQL statements (useful in local dev)
    connect_args=connect_args,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency generator yielding active database sessions.
    Automatically commits, rolls back on error, and closes the session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error("Database transaction rolled back due to error", exc_info=True)
            raise e
        finally:
            await session.close()


async def check_db_health() -> bool:
    """
    Executes a simple SELECT 1 query to check database connectivity.
    """
    try:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

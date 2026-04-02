"""
Khufra Trading System - Database Connection Manager
Handles database connections and session management.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
import logging

from database.models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and provides session handling."""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self._is_sqlite = "sqlite" in database_url.lower()

    async def connect(self):
        """Establish database connection and create tables."""
        try:
            logger.info("Connecting to database...")

            if self._is_sqlite:
                self.engine = create_engine(
                    self.database_url,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool,
                    echo=False
                )
            else:
                self.engine = create_engine(
                    self.database_url,
                    pool_pre_ping=True,
                    pool_size=10,
                    max_overflow=20,
                    echo=False
                )

            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created/verified")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to database: {e}", exc_info=True)
            raise

    async def disconnect(self):
        """Close database connection."""
        try:
            if self.engine:
                self.engine.dispose()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}", exc_info=True)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session with automatic cleanup."""
        if not self.SessionLocal:
            raise RuntimeError("Database not connected. Call connect() first.")
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}", exc_info=True)
            raise
        finally:
            session.close()

    def health_check(self) -> bool:
        """Check if database connection is healthy."""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

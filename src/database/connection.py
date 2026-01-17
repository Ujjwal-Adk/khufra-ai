"""
Project Khufra AI - Database Connection Manager
Handles database connections and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
import logging

from src.database.models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages database connections and provides session handling.
    """

    def __init__(self, database_url: str):
        """
        Initialize database manager.

        Args:
            database_url: SQLAlchemy database URL
        """
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self._is_sqlite = "sqlite" in database_url.lower()

    async def connect(self):
        """
        Establish database connection and create tables.
        """
        try:
            logger.info(f"Connecting to database...")

            # Create engine with appropriate settings
            if self._is_sqlite:
                # SQLite specific settings
                self.engine = create_engine(
                    self.database_url,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool,
                    echo=False  # Set to True for SQL query logging
                )
            else:
                # PostgreSQL or other databases
                self.engine = create_engine(
                    self.database_url,
                    pool_pre_ping=True,  # Verify connections before using
                    pool_size=10,
                    max_overflow=20,
                    echo=False
                )

            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            logger.info("✓ Database tables created/verified successfully")

            return True

        except Exception as e:
            logger.error(f"Failed to connect to database: {e}", exc_info=True)
            raise

    async def disconnect(self):
        """
        Close database connection.
        """
        try:
            if self.engine:
                self.engine.dispose()
                logger.info("✓ Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}", exc_info=True)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a database session with automatic cleanup.

        Usage:
            with db_manager.get_session() as session:
                # Use session here
                session.add(trade)
                session.commit()

        Yields:
            Session: SQLAlchemy session
        """
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

    def execute_with_session(self, func, *args, **kwargs):
        """
        Execute a function with a database session.

        Args:
            func: Function to execute (must accept session as first argument)
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            Result from the function

        Example:
            def create_trade(session, trade_data):
                trade = Trade(**trade_data)
                session.add(trade)
                return trade

            result = db_manager.execute_with_session(create_trade, trade_data)
        """
        with self.get_session() as session:
            return func(session, *args, **kwargs)

    def health_check(self) -> bool:
        """
        Check if database connection is healthy.

        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    def get_table_names(self) -> list:
        """
        Get list of all table names in the database.

        Returns:
            list: List of table names
        """
        try:
            return Base.metadata.tables.keys()
        except Exception as e:
            logger.error(f"Failed to get table names: {e}")
            return []

    def drop_all_tables(self):
        """
        Drop all tables from the database.
        ⚠️ DANGER: This will delete all data!
        """
        if not self.engine:
            raise RuntimeError("Database not connected")

        logger.warning("⚠️  Dropping all tables from database!")
        Base.metadata.drop_all(bind=self.engine)
        logger.info("All tables dropped")

    def recreate_tables(self):
        """
        Drop and recreate all tables.
        ⚠️ DANGER: This will delete all data!
        """
        logger.warning("⚠️  Recreating all database tables!")
        self.drop_all_tables()
        Base.metadata.create_all(bind=self.engine)
        logger.info("Tables recreated successfully")

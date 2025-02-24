from urllib.parse import urlparse

from src.core.db import DatabaseInterface
from src.db.postgres_db import PostgreSQLDatabase
from src.db.trino_db import TrinoDatabase
from src.utils.config import DATABASE_URL
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseConnection:
    def __init__(self):
        self._db: DatabaseInterface | None = None

    async def initialize(self) -> None:
        """Initialize database connection"""
        try:
            logger.info("Initializing database connection...")

            # Parse the connection URL
            parsed = urlparse(DATABASE_URL)

            # Create appropriate database instance based on URL scheme
            if parsed.scheme.startswith("postgresql"):
                self._db = PostgreSQLDatabase(DATABASE_URL)
            elif parsed.scheme == "trino":
                self._db = TrinoDatabase(DATABASE_URL)
            else:
                raise ValueError(f"Unsupported database type: {parsed.scheme}")

            await self._db.initialize()
            logger.info(f"Database connection initialized: {self._db.database_type}")

        except Exception as e:
            logger.error(f"Failed to initialize database connection: {str(e)}")
            raise

    async def shutdown(self) -> None:
        """Close database connection"""
        try:
            if self._db:
                await self._db.shutdown()
        except Exception as e:
            logger.error(f"Error during database shutdown: {str(e)}")
            raise

    async def execute_query(self, query: str) -> list:
        """Execute a query and return results"""
        if not self._db:
            raise ValueError("Database not initialized")
        return await self._db.execute_query(query)

    @property
    def engine(self):
        """Get the database engine/connection"""
        if not self._db:
            raise ValueError("Database not initialized")

        if isinstance(self._db, PostgreSQLDatabase):
            return self._db.engine
        if isinstance(self._db, TrinoDatabase):
            return self._db.connection

        raise ValueError(f"Unsupported database type: {type(self._db)}")

    @property
    def database_type(self) -> str:
        """Get the current database type"""
        return self._db.database_type if self._db else "unknown"

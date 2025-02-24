import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text
from urllib.parse import urlparse, parse_qs
from src.utils.logger import get_logger
from src.utils.config import DATABASE_URL
import trino
from typing import Optional, Union
from enum import Enum

logger = get_logger(__name__)

class DatabaseType(Enum):
    POSTGRESQL = "postgresql"
    TRINO = "trino"

class DatabaseConnection:
    def __init__(self):
        self.engine: Optional[Union[AsyncEngine, trino.dbapi.Connection]] = None
        self.async_session: Optional[async_sessionmaker[AsyncSession]] = None
        self.db_type: Optional[DatabaseType] = None

    async def initialize(self) -> None:
        """Initialize database connection"""
        try:
            logger.info("Initializing database connection...")

            # Parse the connection URL
            parsed = urlparse(DATABASE_URL)

            # Determine database type from URL scheme
            if parsed.scheme.startswith("postgresql"):
                await self._init_postgresql(parsed)
            elif parsed.scheme == "trino":
                await self._init_trino(parsed)
            else:
                raise ValueError(f"Unsupported database type: {parsed.scheme}")

        except Exception as e:
            logger.error(f"Failed to initialize database connection: {str(e)}")
            raise

    async def _init_postgresql(self, parsed_url: urlparse) -> None:
        """Initialize PostgreSQL connection"""
        self.db_type = DatabaseType.POSTGRESQL

        # Parse and filter query parameters
        query_params = parse_qs(parsed_url.query)
        filtered_params = {k: v[0] for k, v in query_params.items() if k != 'sslmode'}

        # Reconstruct the URL
        cleaned_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        if filtered_params:
            cleaned_url += '?' + '&'.join(f'{k}={v}' for k, v in filtered_params.items())

        # Convert to async format if needed
        if cleaned_url.startswith("postgresql://"):
            cleaned_url = cleaned_url.replace("postgresql://", "postgresql+asyncpg://")
            logger.info("Converted database URL to async format")

        logger.info("Creating async PostgreSQL engine...")
        self.engine = create_async_engine(
            cleaned_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            echo=False
        )

        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        # Test the connection
        async with self.engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("PostgreSQL connection test successful")

    async def _init_trino(self, parsed_url: urlparse) -> None:
        """Initialize Trino connection"""
        self.db_type = DatabaseType.TRINO

        # Parse Trino connection parameters
        query_params = parse_qs(parsed_url.query)
        catalog = query_params.get('catalog', ['default'])[0]
        schema = query_params.get('schema', ['public'])[0]

        # Extract username from netloc or query params
        user = query_params.get('user', [None])[0]
        if not user and '@' in parsed_url.netloc:
            user = parsed_url.netloc.split('@')[0]

        # Create Trino connection
        host = parsed_url.hostname
        port = parsed_url.port or 8080

        logger.info(f"Creating Trino connection to {host}:{port}")
        self.engine = trino.dbapi.connect(
            host=host,
            port=port,
            user=user,
            catalog=catalog,
            schema=schema
        )

        # Test the connection
        with self.engine.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result and result[0] == 1:
                logger.info("Trino connection test successful")
            else:
                raise Exception("Trino connection test failed")

    async def shutdown(self) -> None:
        """Close database connection"""
        try:
            if self.engine:
                logger.info("Shutting down database connection...")
                if self.db_type == DatabaseType.POSTGRESQL:
                    await self.engine.dispose()
                elif self.db_type == DatabaseType.TRINO:
                    self.engine.close()
                logger.info("Database connection closed successfully")
        except Exception as e:
            logger.error(f"Error during database shutdown: {str(e)}")
            raise

    async def execute_query(self, query: str) -> list:
        """Execute a query and return results"""
        try:
            if self.db_type == DatabaseType.POSTGRESQL:
                async with self.engine.connect() as conn:
                    result = await conn.execute(text(query))
                    return [dict(row) for row in result]
            elif self.db_type == DatabaseType.TRINO:
                with self.engine.cursor() as cursor:
                    cursor.execute(query)
                    columns = [desc[0] for desc in cursor.description]
                    return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise
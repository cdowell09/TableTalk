from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text
from urllib.parse import urlparse, parse_qs

from src.core.db import DatabaseInterface
from src.utils.logger import get_logger

logger = get_logger(__name__)

class PostgreSQLDatabase(DatabaseInterface):
    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self._engine: Optional[AsyncEngine] = None
        self._async_session: Optional[async_sessionmaker[AsyncSession]] = None
        self._connected = False

    async def initialize(self) -> None:
        try:
            # Parse and filter query parameters
            parsed = urlparse(self.connection_url)
            query_params = parse_qs(parsed.query)
            filtered_params = {k: v[0] for k, v in query_params.items() if k != 'sslmode'}

            # Reconstruct the URL
            cleaned_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if filtered_params:
                cleaned_url += '?' + '&'.join(f'{k}={v}' for k, v in filtered_params.items())

            # Convert to async format if needed
            if cleaned_url.startswith("postgresql://"):
                cleaned_url = cleaned_url.replace("postgresql://", "postgresql+asyncpg://")
                logger.info("Converted database URL to async format")

            logger.info("Creating async PostgreSQL engine...")
            self._engine = create_async_engine(
                cleaned_url,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                echo=False
            )

            self._async_session = async_sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            await self.test_connection()
            self._connected = True
            logger.info("PostgreSQL connection initialized successfully")

        except Exception as e:
            self._connected = False
            logger.error(f"Failed to initialize PostgreSQL connection: {str(e)}")
            raise

    async def shutdown(self) -> None:
        try:
            if self._engine:
                logger.info("Shutting down PostgreSQL connection...")
                await self._engine.dispose()
                self._connected = False
                logger.info("PostgreSQL connection closed successfully")
        except Exception as e:
            logger.error(f"Error during PostgreSQL shutdown: {str(e)}")
            raise

    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        if not self._engine:
            raise ValueError("Database not initialized")
        
        async with self._engine.connect() as conn:
            result = await conn.execute(text(query))
            return [dict(row) for row in result]

    async def test_connection(self) -> bool:
        try:
            if self._engine:
                async with self._engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                    logger.info("PostgreSQL connection test successful")
                    return True
            return False
        except Exception as e:
            logger.error(f"PostgreSQL connection test failed: {str(e)}")
            return False

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def database_type(self) -> str:
        return "postgresql"

    @property
    def engine(self) -> AsyncEngine:
        """Get the SQLAlchemy engine"""
        if not self._engine:
            raise ValueError("Database not initialized")
        return self._engine

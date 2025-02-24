import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text
from urllib.parse import urlparse, parse_qs
from src.utils.logger import get_logger
from src.utils.config import DATABASE_URL

logger = get_logger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.engine: AsyncEngine = None
        self.async_session: async_sessionmaker[AsyncSession] = None

    async def initialize(self) -> None:
        """Initialize database connection"""
        try:
            logger.info("Initializing database connection...")

            # Parse the URL to remove sslmode parameter
            parsed = urlparse(DATABASE_URL)
            query_params = parse_qs(parsed.query)
            filtered_params = {k: v[0] for k, v in query_params.items() if k != 'sslmode'}

            # Reconstruct the URL without sslmode
            cleaned_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if filtered_params:
                cleaned_url += '?' + '&'.join(f'{k}={v}' for k, v in filtered_params.items())

            # Convert database URL to async format if needed
            if cleaned_url.startswith("postgresql://"):
                cleaned_url = cleaned_url.replace("postgresql://", "postgresql+asyncpg://")
                logger.info("Converted database URL to async format")

            logger.info("Creating async engine...")
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

            # Test the connection using SQLAlchemy text()
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                logger.info("Database connection test successful")

        except Exception as e:
            logger.error(f"Failed to initialize database connection: {str(e)}")
            raise

    async def shutdown(self) -> None:
        """Close database connection"""
        try:
            if self.engine:
                logger.info("Shutting down database connection...")
                await self.engine.dispose()
                logger.info("Database connection closed successfully")
        except Exception as e:
            logger.error(f"Error during database shutdown: {str(e)}")
            raise
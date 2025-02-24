from typing import Any
from urllib.parse import parse_qs, urlparse

import trino

from src.core.db import DatabaseInterface
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TrinoDatabase(DatabaseInterface):
    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self._connection: trino.dbapi.Connection | None = None
        self._connected = False
        self._parsed_url = urlparse(connection_url)

    async def initialize(self) -> None:
        try:
            # Parse Trino connection parameters
            query_params = parse_qs(self._parsed_url.query)
            catalog = query_params.get("catalog", ["default"])[0]
            schema = query_params.get("schema", ["public"])[0]

            # Extract username from netloc or query params
            user = query_params.get("user", [None])[0]
            if not user and "@" in self._parsed_url.netloc:
                user = self._parsed_url.netloc.split("@")[0]

            host = self._parsed_url.hostname
            port = self._parsed_url.port or 8080

            logger.info(f"Creating Trino connection to {host}:{port}")
            self._connection = trino.dbapi.connect(
                host=host, port=port, user=user, catalog=catalog, schema=schema
            )

            await self.test_connection()
            self._connected = True
            logger.info("Trino connection initialized successfully")

        except Exception as e:
            self._connected = False
            logger.error(f"Failed to initialize Trino connection: {str(e)}")
            raise

    async def shutdown(self) -> None:
        try:
            if self._connection:
                logger.info("Shutting down Trino connection...")
                self._connection.close()
                self._connected = False
                logger.info("Trino connection closed successfully")
        except Exception as e:
            logger.error(f"Error during Trino shutdown: {str(e)}")
            raise

    async def execute_query(self, query: str) -> list[dict[str, Any]]:
        if not self._connection:
            raise ValueError("Database not initialized")

        with self._connection.cursor() as cursor:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]

    async def test_connection(self) -> bool:
        try:
            if self._connection:
                with self._connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    if result and result[0] == 1:
                        logger.info("Trino connection test successful")
                        return True
            return False
        except Exception as e:
            logger.error(f"Trino connection test failed: {str(e)}")
            return False

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def database_type(self) -> str:
        return "trino"

    @property
    def connection(self) -> trino.dbapi.Connection:
        """Get the Trino connection"""
        if not self._connection:
            raise ValueError("Database not initialized")
        return self._connection

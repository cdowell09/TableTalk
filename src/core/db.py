from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum
from src.core.base import BaseResponse

class DatabaseType(Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    TRINO = "trino"

class DatabaseInterface(ABC):
    """Abstract base class for database connections"""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize database connection"""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Close database connection"""
        pass

    @abstractmethod
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a query and return results"""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if the connection is working"""
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if database is connected"""
        pass

    @property
    @abstractmethod
    def database_type(self) -> str:
        """Get the type of database"""
        pass
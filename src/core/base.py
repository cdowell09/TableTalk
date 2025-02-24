from abc import ABC, abstractmethod
from typing import Dict, Optional

class BaseResponse:
    def __init__(self, success: bool, data: Optional[Dict] = None, error: Optional[str] = None):
        self.success = success
        self.data = data or {}
        self.error = error

class BaseProvider(ABC):
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider"""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Cleanup provider resources"""
        pass

class BaseLLMProvider(BaseProvider):
    @abstractmethod
    async def generate_sql(self, prompt: str, metadata: Dict) -> BaseResponse:
        """Generate SQL from natural language"""
        pass

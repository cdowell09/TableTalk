from abc import ABC, abstractmethod


class BaseResponse:
    def __init__(
        self, success: bool, data: dict | None = None, error: str | None = None
    ):
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
    async def generate_sql(self, prompt: str, metadata: dict) -> BaseResponse:
        """Generate SQL from natural language"""
        pass

from typing import Dict, Optional, Protocol
from src.core.base import BaseResponse

class LLMProvider(Protocol):
    async def generate_sql(self, prompt: str, metadata: Dict) -> BaseResponse:
        """Protocol for LLM providers"""
        pass

class LLMConfig:
    def __init__(
        self,
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 1000,
        timeout: int = 30,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

import os
from typing import Dict
import json
from openai import AsyncOpenAI
from src.core.base import BaseResponse, BaseLLMProvider
from src.core.llm_provider import LLMConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)

class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
        self.config = LLMConfig(model="gpt-4o")
        self.client = None

    async def initialize(self) -> None:
        """Initialize OpenAI client"""
        try:
            logger.info("Initializing OpenAI provider...")
            self.client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            logger.info("OpenAI provider initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {str(e)}")
            raise

    async def shutdown(self) -> None:
        """Cleanup resources"""
        logger.info("Shutting down OpenAI provider")
        self.client = None

    async def generate_sql(self, prompt: str, metadata: Dict) -> BaseResponse:
        try:
            if not self.client:
                raise ValueError("OpenAI client not initialized")

            system_prompt = (
                "You are an expert SQL generator. Generate PostgreSQL queries based on "
                "natural language input and database schema metadata. Return only valid SQL "
                "in a JSON response with a 'sql' key."
            )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Schema metadata: {json.dumps(metadata)}\nQuery: {prompt}"}
            ]

            logger.debug(f"Sending request to OpenAI with prompt: {prompt}")
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                response_format={"type": "json_object"}
            )

            sql = json.loads(response.choices[0].message.content)["sql"]
            logger.info(f"Successfully generated SQL: {sql}")
            return BaseResponse(success=True, data={"sql": sql})

        except Exception as e:
            logger.error(f"Failed to generate SQL: {str(e)}")
            return BaseResponse(success=False, error=str(e))
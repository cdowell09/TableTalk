import os
from typing import Dict
import json
from openai import AsyncOpenAI
from src.core.base import BaseResponse, BaseLLMProvider
from src.core.llm_provider import LLMConfig
from src.core.prompts import PromptManager
from src.utils.logger import get_logger

# Get a named logger instance for this module
logger = get_logger("openai_provider")

class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        self.config = LLMConfig(model="gpt-4o")
        self.client = None
        self.prompt_manager = PromptManager()

    async def initialize(self) -> None:
        """Initialize OpenAI client"""
        try:
            logger.info("Initializing OpenAI provider...")
            self.client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            logger.info("OpenAI provider initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {e}")
            raise

    async def shutdown(self) -> None:
        """Cleanup resources"""
        logger.info("Shutting down OpenAI provider")
        self.client = None

    async def generate_sql(self, prompt: str, metadata: Dict) -> BaseResponse:
        try:
            if not self.client:
                raise ValueError("OpenAI client not initialized")

            # Prepare variables for the prompt template
            variables = {
                "query": prompt,
                "metadata": json.dumps(metadata),
                "context": "Generate a PostgreSQL query based on the following request."
            }

            # Generate the full prompt using the template
            rendered_prompt = self.prompt_manager.render_prompt(
                "sql_generation", variables
            )

            logger.debug(f"Sending request to OpenAI with prompt: {prompt}")
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "user", "content": rendered_prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                response_format={"type": "json_object"}
            )

            sql = json.loads(response.choices[0].message.content)["sql"]
            logger.info("Successfully generated SQL query")
            logger.debug(f"Generated SQL: {sql}")
            return BaseResponse(success=True, data={"sql": sql})

        except Exception as e:
            logger.error(f"Failed to generate SQL: {e}")
            return BaseResponse(success=False, error=str(e))
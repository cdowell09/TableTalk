import json

from openai import AsyncOpenAI

from src.core.base import BaseLLMProvider, BaseResponse
from src.core.db import DatabaseType
from src.core.llm_provider import LLMConfig
from src.core.prompts import PromptManager
from src.utils.config import OPENAI_API_KEY, OPENAI_MODEL
from src.utils.logger import get_logger

# Get a named logger instance for this module
logger = get_logger("openai_provider")


class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.config = LLMConfig(model=OPENAI_MODEL)
        self.client = None
        self.prompt_manager = PromptManager()

    async def initialize(self) -> None:
        """Initialize OpenAI client"""
        try:
            logger.info("Initializing OpenAI provider...")
            logger.info(f"Using OpenAI model: {self.config.model}")
            self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            logger.info("OpenAI provider initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {e}")
            raise RuntimeError("Failed to initialize OpenAI provider") from e

    async def shutdown(self) -> None:
        """Cleanup resources"""
        logger.info("Shutting down OpenAI provider")
        self.client = None

    async def generate_sql(self, prompt: str, metadata: dict) -> BaseResponse:
        try:
            if not self.client:
                raise ValueError("OpenAI client not initialized")

            # Determine database type from metadata or fall back to PostgreSQL
            database_type = metadata.get("database_type", DatabaseType.POSTGRESQL.value)

            # Prepare variables for the prompt template
            variables = {
                "query": prompt,
                "metadata": json.dumps(metadata),
                "database_type": database_type,
                "context": (
                    f"Generate a {database_type} query based on the following request."
                ),
            }

            # Generate the full prompt using the template
            rendered_prompt = self.prompt_manager.render_prompt(
                "sql_generation", variables
            )

            logger.debug(f"Sending request to OpenAI with prompt: {prompt}")
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": rendered_prompt}],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                response_format={"type": "json_object"},
            )

            sql = json.loads(response.choices[0].message.content)["sql"]
            logger.info("Successfully generated SQL query")
            logger.debug(f"Generated SQL: {sql}")
            return BaseResponse(success=True, data={"sql": sql})

        except Exception as e:
            logger.error(f"Failed to generate SQL: {e}")
            return BaseResponse(success=False, error=str(e))

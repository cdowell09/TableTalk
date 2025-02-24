import os
import json
import aiohttp
from typing import Dict
from src.core.base import BaseResponse, BaseLLMProvider
from src.core.llm_provider import LLMConfig
from src.core.prompts import PromptManager
from src.utils.logger import get_logger
from src.utils.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from src.core.db import DatabaseType

logger = get_logger("ollama_provider")

class OllamaProvider(BaseLLMProvider):
    def __init__(self):
        # Default to "llama2" if not specified
        self.config = LLMConfig(model=OLLAMA_MODEL or "llama2")
        self.base_url = OLLAMA_BASE_URL or "http://localhost:11434"
        self.session = None
        self.prompt_manager = PromptManager()

    async def initialize(self) -> None:
        """Initialize Ollama client session"""
        try:
            logger.info("Initializing Ollama provider...")
            logger.info(f"Using Ollama model: {self.config.model}")
            self.session = aiohttp.ClientSession()
            # Test connection
            async with self.session.get(f"{self.base_url}/api/version") as response:
                if response.status != 200:
                    raise ConnectionError("Failed to connect to Ollama service")
            logger.info("Ollama provider initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama provider: {e}")
            raise

    async def shutdown(self) -> None:
        """Cleanup resources"""
        logger.info("Shutting down Ollama provider")
        if self.session:
            await self.session.close()
        self.session = None

    async def generate_sql(self, prompt: str, metadata: Dict) -> BaseResponse:
        try:
            if not self.session:
                raise ValueError("Ollama client not initialized")

            # Determine database type from metadata or fall back to PostgreSQL
            database_type = metadata.get('database_type', DatabaseType.POSTGRESQL.value)

            # Prepare variables for the prompt template
            variables = {
                "query": prompt,
                "metadata": json.dumps(metadata),
                "database_type": database_type,
                "context": f"Generate a {database_type} query based on the following request."
            }

            # Generate the full prompt using the template
            rendered_prompt = self.prompt_manager.render_prompt(
                "sql_generation", variables
            )

            logger.debug(f"Sending request to Ollama with prompt: {prompt}")

            # Make request to Ollama API
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.config.model,
                    "prompt": rendered_prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.config.temperature,
                    }
                }
            ) as response:
                if response.status != 200:
                    raise Exception(f"Ollama API error: {response.status}")

                result = await response.json()
                response_text = result.get("response", "")

                # Try to extract SQL from the response
                sql = None
                try:
                    # First attempt: try to parse as JSON
                    start_idx = response_text.find("{")
                    end_idx = response_text.rfind("}") + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = response_text[start_idx:end_idx]
                        parsed_json = json.loads(json_str)
                        sql = parsed_json.get("sql")
                except json.JSONDecodeError:
                    pass

                # If JSON parsing failed or no SQL found, use the raw response
                if not sql:
                    sql = response_text.strip()

                logger.info("Successfully generated SQL query")
                logger.debug(f"Generated SQL: {sql}")
                return BaseResponse(success=True, data={"sql": sql})

        except Exception as e:
            logger.error(f"Failed to generate SQL: {e}")
            return BaseResponse(success=False, error=str(e))
from src.core.base import BaseResponse
from src.core.llm_provider import LLMProvider
from src.core.prompts import PromptManager


class SQLGenerator:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.prompt_manager = PromptManager()

    async def generate_sql(
        self, query: str, metadata: dict, context: dict | None = None
    ) -> BaseResponse:
        """Generate SQL from natural language query"""
        try:
            # Prepare variables for the prompt template
            variables = {
                "query": query,
                "metadata": metadata,
                "context": context or {},
            }

            # Generate SQL using LLM
            response = await self.llm_provider.generate_sql(
                prompt=query, metadata=metadata
            )

            if not response.success:
                return response

            return BaseResponse(success=True, data={"sql": response.data["sql"]})

        except Exception as e:
            return BaseResponse(success=False, error=str(e))
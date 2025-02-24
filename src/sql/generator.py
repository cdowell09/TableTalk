from src.core.base import BaseResponse
from src.core.llm_provider import LLMProvider


class SQLGenerator:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    async def generate_sql(
        self, query: str, metadata: dict, context: dict | None = None
    ) -> BaseResponse:
        """Generate SQL from natural language query"""
        try:
            # Enhance prompt with context if provided
            enhanced_prompt = self._build_prompt(query, context)

            # Generate SQL using LLM
            response = await self.llm_provider.generate_sql(
                prompt=enhanced_prompt, metadata=metadata
            )

            if not response.success:
                return response

            return BaseResponse(success=True, data={"sql": response.data["sql"]})

        except Exception as e:
            return BaseResponse(success=False, error=str(e))

    def _build_prompt(self, query: str, context: dict | None = None) -> str:
        """Build enhanced prompt with context"""
        prompt = f"Convert this question to SQL: {query}"

        if context:
            prompt = f"{prompt}\nAdditional context: {context}"

        return prompt

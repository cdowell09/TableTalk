"""Module for managing prompt templates and rendering."""
from typing import Dict, Optional
from string import Template


class PromptTemplate:
    def __init__(self, template: str):
        self.template = Template(template)

    def render(self, variables: Optional[Dict] = None) -> str:
        """Render the template with provided variables."""
        try:
            return self.template.safe_substitute(variables or {})
        except KeyError as e:
            raise ValueError(f"Missing required variable in template: {e}")


# System prompts
SQL_GENERATION_PROMPT = PromptTemplate(
    template=(
        "You are an expert SQL generator. Generate valid SQL queries based on "
        "natural language input and database schema metadata. The target database "
        "type is $database_type. Return only valid SQL in a JSON response with a "
        "'sql' key.\n\n"
        "Additional context: $context\n"
        "Schema metadata: $metadata\n"
        "Query: $query"
    )
)

# Default prompts dictionary
DEFAULT_PROMPTS = {
    "sql_generation": SQL_GENERATION_PROMPT,
}


class PromptManager:
    def __init__(self, custom_prompts: Optional[Dict[str, PromptTemplate]] = None):
        """Initialize with default prompts and optional custom prompts."""
        self.prompts = DEFAULT_PROMPTS.copy()
        if custom_prompts:
            self.prompts.update(custom_prompts)

    def get_prompt(self, prompt_name: str) -> PromptTemplate:
        """Get a prompt template by name."""
        if prompt_name not in self.prompts:
            raise KeyError(f"Prompt template '{prompt_name}' not found")
        return self.prompts[prompt_name]

    def add_prompt(self, name: str, template: str) -> None:
        """Add a new prompt template."""
        self.prompts[name] = PromptTemplate(template)

    def render_prompt(self, prompt_name: str, variables: Optional[Dict] = None) -> str:
        """Render a prompt template with provided variables."""
        template = self.get_prompt(prompt_name)
        return template.render(variables)
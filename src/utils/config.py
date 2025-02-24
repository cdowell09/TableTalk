import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
dotenv_path = Path('.env')
if dotenv_path.exists():
    load_dotenv(dotenv_path)

def get_env_variable(key: str, default: str | None = None) -> str:
    """
    Get an environment variable with error handling
    """
    value = os.environ.get(key, default)
    if value is None:
        raise ValueError(f"Environment variable {key} is not set")
    return value

# OpenAI Configuration
OPENAI_API_KEY = get_env_variable("OPENAI_API_KEY")
OPENAI_MODEL = get_env_variable("OPENAI_MODEL", "gpt-4o")

# Ollama Configuration
OLLAMA_BASE_URL = get_env_variable("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = get_env_variable("OLLAMA_MODEL", "llama2")

# Database Configuration
DATABASE_URL = get_env_variable("DATABASE_URL")
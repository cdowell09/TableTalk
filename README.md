# Text2SQL Backend Service

A modular Text2SQL backend service that leverages advanced AI models (OpenAI and Ollama) to convert natural language queries into valid SQL statements. The service includes dynamic metadata retrieval, multiple database support, and advanced logging capabilities.

## Features

- Natural language to SQL conversion using multiple LLM providers:
  - OpenAI GPT models
  - Ollama local models
- Multi-database support:
  - PostgreSQL
  - Trino
- SQL validation and security checks
- Dynamic database metadata handling
- Structured logging with Loguru
- FastAPI-based REST API
- Async database operations
- Environment configuration using python-dotenv
- Code quality enforcement using Ruff
- Flexible provider abstraction for database and LLM integrations

## Project Structure

```
src/
├── api/               # API routes and models
│   ├── models.py     # Pydantic models for request/response
│   └── routes.py     # API endpoints
├── core/             # Core functionality and protocols
│   ├── base.py       # Base classes and protocols
│   └── provider.py   # Provider interfaces (DB & LLM)
├── db/               # Database related code
│   ├── postgres_db.py # PostgreSQL implementation
│   └── trino_db.py   # Trino implementation
├── llm/              # LLM providers
│   ├── openai_provider.py  # OpenAI implementation
│   └── ollama_provider.py  # Ollama implementation
├── sql/
│   ├── validator.py  # SQL validation logic
│   └── generator.py  # SQL generation utilities
└── utils/
    ├── logger.py     # Logging configuration
    └── config.py     # Environment configuration
```

## Setup

1. Clone the repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your configuration:
```bash
# Create .env file from example
cp .env.example .env

# Edit .env file with your values
# Required environment variables:
OPENAI_API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:password@host:port/dbname
# Or for Trino:
# DATABASE_URL=trino://user@host:port/catalog/schema

# Optional environment variables:
OPENAI_MODEL=gpt-4  # Defaults to gpt-4 if not set
OLLAMA_BASE_URL=http://localhost:11434  # For local Ollama setup
OLLAMA_MODEL=llama2  # Specify Ollama model to use
```

4. Start the server:
```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --log-level debug
```

## Usage

### Converting Natural Language to SQL

Send a POST request to `/api/query` with your natural language query:

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find all users who signed up last month",
    "context": {
      "users": {
        "columns": ["id", "username", "email", "created_at"],
        "relationships": []
      }
    }
  }'
```

#### Understanding the Context Payload

The `context` field is a required parameter that provides the LLM with necessary information about your database schema. This context helps the model generate accurate and valid SQL queries.

Structure:
```json
{
  "context": {
    "table_name": {
      "columns": ["column1", "column2", ...],
      "relationships": [
        {
          "referenced_table": "other_table",
          "type": "many_to_one",
          "foreign_key": "other_table_id"
        }
      ]
    }
  }
}
```

Key components:
- `table_name`: The name of each table in your schema
- `columns`: Array of column names in the table
- `relationships`: (Optional) Array of relationships with other tables
  - `referenced_table`: The name of the related table
  - `type`: Relationship type ("one_to_many", "many_to_one", "one_to_one")
  - `foreign_key`: The column name that serves as the foreign key

Example with relationships:
```json
{
  "query": "Show me all orders with their customer details",
  "context": {
    "orders": {
      "columns": ["id", "total_amount", "customer_id", "created_at"],
      "relationships": [
        {
          "referenced_table": "customers",
          "type": "many_to_one",
          "foreign_key": "customer_id"
        }
      ]
    },
    "customers": {
      "columns": ["id", "name", "email"],
      "relationships": []
    }
  }
}
```

Response:
```json
{
  "success": true,
  "sql": "SELECT * FROM users WHERE created_at >= date_trunc('month', current_date - interval '1 month') AND created_at < date_trunc('month', current_date)"
}
```

Note: The context payload is required for all queries as it helps the LLM understand your database structure and generate appropriate SQL. Without it, the service cannot guarantee accurate SQL generation.

## Key Components

### LLM Providers
- Multiple provider support (OpenAI, Ollama)
- Configurable model selection and parameters
- Structured error handling
- Provider abstraction for easy integration of new LLMs

### Database Support
- Multiple database engine support
- PostgreSQL for traditional relational databases
- Trino for data warehouse queries
- Abstract provider interface for adding new engines

### SQL Validator
- Prevents dangerous operations (DROP, DELETE, etc.)
- Validates table and column names against metadata
- Ensures SQL syntax correctness

### Logging System
- Structured logging using Loguru
- Configurable log levels and formats
- Comprehensive error tracking

## Development Guidelines

1. **Code Quality**
   - Use Ruff for code formatting and linting
   - Follow PEP 8 style guidelines
   - Maintain consistent code formatting

2. **Logging**
   - Use the provided logger from `src/utils/logger.py`
   - Include appropriate log levels (DEBUG, INFO, WARNING, ERROR)
   - Add context when logging errors

3. **Error Handling**
   - Use the BaseResponse class for consistent error responses
   - Include detailed error messages for debugging
   - Handle both API and processing errors gracefully

4. **Database Operations**
   - Use async database operations
   - Validate metadata before generating SQL
   - Follow SQL injection prevention best practices
   - Use appropriate database provider for the use case

5. **Provider Implementation**
   - Follow the provider interfaces in `core/provider.py`
   - Implement required methods and error handling
   - Add comprehensive tests for new providers

## Contributing

1. Create a feature branch
2. Add appropriate tests
3. Update documentation
4. Submit a pull request

## License

MIT License
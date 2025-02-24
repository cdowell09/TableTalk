# Text2SQL Backend Service

A modular Text2SQL backend service that leverages OpenAI's GPT models to convert natural language queries into valid SQL statements. The service includes dynamic metadata retrieval and advanced logging capabilities.

## Features

- Natural language to SQL conversion using OpenAI GPT models
- SQL validation and security checks
- Dynamic database metadata handling
- Structured logging with Loguru
- FastAPI-based REST API
- Async database operations

## Project Structure

```
src/
├── api/               # API routes and models
│   ├── models.py     # Pydantic models for request/response
│   └── routes.py     # API endpoints
├── core/             # Core functionality and protocols
│   ├── base.py       # Base classes and protocols
│   └── llm_provider.py # LLM provider interface
├── db/               # Database related code
├── llm/
│   └── openai_provider.py # OpenAI implementation
├── sql/
│   ├── validator.py  # SQL validation logic
│   └── generator.py  # SQL generation utilities
└── utils/
    └── logger.py     # Logging configuration
```

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_api_key_here

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/dbname
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

Response:
```json
{
  "success": true,
  "sql": "SELECT * FROM users WHERE created_at >= date_trunc('month', current_date - interval '1 month') AND created_at < date_trunc('month', current_date)"
}
```

## Key Components

### LLM Provider
- Handles communication with OpenAI's API
- Configurable model selection and parameters
- Structured error handling

### SQL Validator
- Prevents dangerous operations (DROP, DELETE, etc.)
- Validates table and column names against metadata
- Ensures SQL syntax correctness

### Logging System
- Structured logging using Loguru
- Configurable log levels and formats
- Comprehensive error tracking

## Development Guidelines

1. **Logging**
   - Use the provided logger from `src/utils/logger.py`
   - Include appropriate log levels (DEBUG, INFO, WARNING, ERROR)
   - Add context when logging errors

2. **Error Handling**
   - Use the BaseResponse class for consistent error responses
   - Include detailed error messages for debugging
   - Handle both API and processing errors gracefully

3. **Database Operations**
   - Use async database operations
   - Validate metadata before generating SQL
   - Follow SQL injection prevention best practices

## Contributing

1. Create a feature branch
2. Add appropriate tests
3. Update documentation
4. Submit a pull request

## License

MIT License

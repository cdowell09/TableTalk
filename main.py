from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from sqlalchemy import text
from src.llm.openai_provider import OpenAIProvider
from src.sql.generator import SQLGenerator
from src.sql.validator import SQLValidator
from src.db.connection import DatabaseConnection
from src.db.metadata import MetadataManager
from src.utils.logger import get_logger

# Configure logger
logger = get_logger(__name__)

app = FastAPI(
    title="Text2SQL API",
    description="Natural Language to SQL Query Converter",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict] = None

class QueryResponse(BaseModel):
    success: bool
    sql: Optional[str] = None
    error: Optional[str] = None

# Initialize components
db_connection = DatabaseConnection()
llm_provider = OpenAIProvider()
sql_generator = SQLGenerator(llm_provider)
sql_validator = SQLValidator()

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI server starting up...")
    try:
        await db_connection.initialize()
        logger.info("Database connection initialized")
        await llm_provider.initialize()
        logger.info("LLM provider initialized")
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("FastAPI server shutting down...")
    try:
        await db_connection.shutdown()
        await llm_provider.shutdown()
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}")
        raise

@app.get("/health")
async def health_check():
    logger.debug("Health check endpoint called")
    try:
        # Test database connection using SQLAlchemy text()
        async with db_connection.engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        logger.info(f"Processing query: {request.query}")

        # Initialize metadata manager and get current schema
        metadata_manager = MetadataManager(db_connection.engine)
        metadata = await metadata_manager.get_table_metadata()

        if not metadata:
            raise ValueError("No database metadata available")

        # Generate SQL
        generation_result = await sql_generator.generate_sql(
            query=request.query,
            metadata=metadata,
            context=request.context
        )

        if not generation_result.success:
            logger.error(f"SQL generation failed: {generation_result.error}")
            return QueryResponse(success=False, error=generation_result.error)

        # Validate SQL
        validation_result = await sql_validator.validate_sql(
            sql=generation_result.data["sql"],
            metadata=metadata
        )

        if not validation_result.success:
            logger.error(f"SQL validation failed: {validation_result.error}")
            return QueryResponse(success=False, error=validation_result.error)

        logger.info(f"Successfully generated SQL: {generation_result.data['sql']}")
        return QueryResponse(
            success=True,
            sql=generation_result.data["sql"]
        )

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="debug")
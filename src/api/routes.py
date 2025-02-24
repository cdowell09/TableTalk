from fastapi import APIRouter, HTTPException, Depends
from src.api.models import QueryRequest, QueryResponse, ErrorResponse
from src.db.metadata import MetadataManager
from src.sql.generator import SQLGenerator
from src.sql.validator import SQLValidator
from src.utils.logger import get_logger
from src.db.connection import DatabaseConnection

router = APIRouter()
logger = get_logger(__name__)

# Database connection instance
db_connection = DatabaseConnection()

# Dependencies
def get_metadata_manager():
    return MetadataManager(db_connection.engine)

def get_llm_provider():
    from src.llm.openai_provider import OpenAIProvider
    return OpenAIProvider()

def get_sql_generator():
    return SQLGenerator(get_llm_provider())

def get_sql_validator():
    return SQLValidator()

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    try:
        # Test database connection
        async with db_connection.engine.connect() as conn:
            await conn.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

@router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    metadata_manager: MetadataManager = Depends(get_metadata_manager),
    sql_generator: SQLGenerator = Depends(get_sql_generator),
    sql_validator: SQLValidator = Depends(get_sql_validator)
):
    try:
        # Get metadata
        metadata = await metadata_manager.get_table_metadata()

        # Generate SQL
        generation_result = await sql_generator.generate_sql(
            query=request.query,
            metadata=metadata,
            context=request.context
        )

        if not generation_result.success:
            logger.error(f"SQL generation failed: {generation_result.error}")
            raise HTTPException(
                status_code=400,
                detail=generation_result.error
            )

        # Validate SQL
        validation_result = await sql_validator.validate_sql(
            sql=generation_result.data["sql"],
            metadata=metadata
        )

        if not validation_result.success:
            logger.error(f"SQL validation failed: {validation_result.error}")
            raise HTTPException(
                status_code=400,
                detail=validation_result.error
            )

        return QueryResponse(
            success=True,
            sql=generation_result.data["sql"]
        )

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
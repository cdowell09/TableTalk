from pydantic import BaseModel
from typing import Dict, Optional

class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict] = None
    prompt_variables: Optional[Dict] = None

class QueryResponse(BaseModel):
    success: bool
    sql: Optional[str] = None
    error: Optional[str] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
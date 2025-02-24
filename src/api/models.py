from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    context: dict | None = None
    prompt_variables: dict | None = None


class QueryResponse(BaseModel):
    success: bool
    sql: str | None = None
    error: str | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str

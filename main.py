from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict

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

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        # For now, return a simple response
        return QueryResponse(
            success=True,
            sql="SELECT * FROM example_table"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
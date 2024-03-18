from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str
    conversation_id: str
    platform_source: str
    tenant_id: str

class QueryResponseError(BaseModel):
    code: int = -1
    message: str = ''

class QueryResponseData(BaseModel):
    answer: str

class QueryResponse(BaseModel):
    error: QueryResponseError | None = None
    data: QueryResponseData | None = None
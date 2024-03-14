from pydantic import BaseModel

class QueryResponseError(BaseModel):
    code: int = -1
    message: str = ''

class QueryResponseData(BaseModel):
    answer: str

class QueryResponse(BaseModel):
    error: QueryResponseError | None = None
    data: QueryResponseData | None = None
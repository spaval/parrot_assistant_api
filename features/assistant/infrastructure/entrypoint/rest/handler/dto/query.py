from enum import Enum
from pydantic import BaseModel

class QueryModeEnum(str, Enum):
    qa = 'qa'
    assistant = 'assistant'

class HistoryModeEnum(str, Enum):
    db = 'db'
    cached = 'cached'

class QueryRequest(BaseModel):
    question: str
    conversation_id: str
    platform_source: str
    tenant_id: str
    query_mode: QueryModeEnum = QueryModeEnum.qa
    history_mode: HistoryModeEnum = HistoryModeEnum.cached

class QueryResponseError(BaseModel):
    code: int = -1
    message: str = ''

class QueryResponseData(BaseModel):
    answer: str

class QueryResponse(BaseModel):
    error: QueryResponseError = None
    data: QueryResponseData = None
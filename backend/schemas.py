# Pydantic schemas for API requests and responses
from pydantic import BaseModel
from typing import Optional

class ChatMessage(BaseModel):
    session_id: str
    user: str
    assistant: str
    user_id: str
    timestamp: Optional[str] = None

class ChatHistoryRequest(BaseModel):
    session_id: str
    user_id: str

class RAGQueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = None

class ExcelIngestRequest(BaseModel):
    container_name: str
    blob_name: str

class AdvancedRAGRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    user_role: Optional[str] = 'user'

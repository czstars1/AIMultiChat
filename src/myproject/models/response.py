from datetime import datetime

from pydantic import BaseModel, Field

class SessionResponse(BaseModel):
    id: str
    name: str
    created_at: datetime=Field(default_factory=datetime.now)
    owner: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str


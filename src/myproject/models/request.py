from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    name: str = Field(...,min_length=1,max_length=50,description="会话名称")

class SessionUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="新的会话名称")

class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, description="会话ID")
    message: str = Field(..., min_length=1, max_length=2000, description="用户消息")

class UserRegister(BaseModel):
    name: str = Field(...,min_length=3,max_length=20)
    password: str = Field(...,min_length=6)

class UserLogin(BaseModel):
    name: str = Field(...,min_length=3,max_length=20)
    password: str = Field(...,min_length=6)

class RAGRequest(BaseModel):
    message: str
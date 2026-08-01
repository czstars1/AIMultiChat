from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse
from src.myproject.dependencies import auth,database
from src.myproject.models.request import ChatRequest
from src.myproject.models.response import ChatResponse
from src.myproject.services import session_service, message_service,llm_service

router = APIRouter(prefix="/chat",tags=["chat"])

@router.post("/")
async def chat_endpoint1(request: ChatRequest,token: str = Depends(auth.verify_token),db:Session =Depends(database.get_db)):
    session = session_service.get_session_by_id(db, request.session_id, token)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or access denied")

    history = message_service.get_messages_by_session(db, request.session_id, limit=10)
    messages = [{"role": msg.role, "content": msg.content} for msg in history]

    messages.append({"role": "user", "content": request.message})
    message_service.add_message(db, request.session_id, "user", request.message)

    reply = await llm_service.call_llm(messages)
    message_service.add_message(db, request.session_id, "assistant", reply)
    return ChatResponse(reply=reply, session_id=request.session_id)

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    token: str = Depends(auth.verify_token),
    db: Session = Depends(database.get_db)  # ✅ 依赖注入获取 db
):
    # 1. 验证会话
    session = session_service.get_session_by_id(db, request.session_id, token)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or access denied")

    # 2. 保存用户消息
    message_service.add_message(db, request.session_id, "user", request.message)

    # 3. 获取历史消息
    history = message_service.get_messages_by_session(db, request.session_id, limit=10)
    messages = [{"role": msg.role, "content": msg.content} for msg in reversed(history)]
    if not messages or messages[0]["role"] != "system":
        messages.insert(0, {
            "role": "system",
            "content": "你是一个智能助手，请始终记住用户之前提出的任何明确要求，并在回答中遵守。"
        })

    # 4. 定义流式事件生成器（闭包捕获 db）
    async def event_stream():
        collected_reply = ""
        try:
            async for chunk in llm_service.stream_llm(messages):
                collected_reply += chunk
                yield f"data: {chunk}\n\n"
            # 保存助手回复
            if collected_reply.strip():
                message_service.add_message(db, request.session_id, "assistant", collected_reply)
        except Exception as error:
            yield f"data: [ERROR] {str(error)}\n\n"
        # 注意：db 由 FastAPI 的依赖注入自动管理（请求结束后自动关闭）

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@router.get("/{session_id}/messages")
def get_messages(
    session_id: str,
    token: str = Depends(auth.verify_token),
    db: Session = Depends(database.get_db)
):

    session = session_service.get_session_by_id(db, session_id, token)
    if not session:

        raise HTTPException(status_code=404, detail="Session not found")
    msgs = message_service.get_messages_by_session(db, session_id, limit=50)

    return [{"role":msg.role,"content":msg.content,"created_at":msg.created_at}for msg in msgs]
import shutil

from fastapi import APIRouter, UploadFile, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pathlib import Path
from src.myproject.services.doc_processor import index_file
from src.myproject.models.request import RAGRequest
from src.myproject.config import DATA_DIR
from src.myproject.dependencies.auth import verify_token
from src.myproject.services.rag_service import rag_ask, rag_ask_stream
import uuid

router = APIRouter(prefix="/rag", tags=["RAG"])

UPLOAD_DIR = DATA_DIR / "knowledge_docs"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_document(
    file: UploadFile,
    token: str = Depends(verify_token)
):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ['.txt', '.pdf', '.docx']:
        raise HTTPException(400, "仅支持 txt, pdf, docx 格式")

    safe_name = f"{uuid.uuid4()}{suffix}"
    file_path = UPLOAD_DIR / safe_name

    # 保存文件
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f, length=1024 * 1024)

    # ✅ 调用统一处理函数

    index_file(str(file_path))  # 内部会切片、向量化、入库

    return {"message": f"文件 {file.filename} 上传成功"}

@router.post("/ask")
async def ask_question(
    request: RAGRequest,               # 接收 JSON 请求体
    token: str = Depends(verify_token)
):
    """非流式 RAG 问答"""
    return await rag_ask(request.message)   # 从 request 中取 message


@router.post("/ask/stream")
async def ask_question_stream(
    request: RAGRequest,               # 接收 JSON 请求体
    token: str = Depends(verify_token)
):
    """流式 RAG 问答，SSE 格式"""
    async def event_stream():
        async for chunk in rag_ask_stream(request.message):   # 传入 message
            yield f"data: {chunk}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
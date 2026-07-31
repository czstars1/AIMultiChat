from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pathlib import Path
from config import DATA_DIR
from dependencies.auth import verify_token
from services.rag_service import rag_ask, rag_ask_stream
from services.doc_processor import read_file, chunk_text
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
import uuid, os

router = APIRouter(prefix="/rag", tags=["RAG"])


CHROMA_DIR = DATA_DIR / "chroma"

client = PersistentClient(path=str(CHROMA_DIR))
collection = client.get_or_create_collection(name="knowledge_base")
model = SentenceTransformer('all-MiniLM-L6-v2')

UPLOAD_DIR = DATA_DIR / "knowledge_docs"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_document(
        file: UploadFile ,
        token: str = Depends(verify_token)
):
    suffix = Path(file.filename).suffix.lower()
    """上传文档并自动索引到知识库"""
    if suffix not in ['.txt', '.pdf', '.docx']:
        raise HTTPException(400, "仅支持 txt, pdf, docx 格式")
    safe_name = f"{uuid.uuid4()}{suffix}"

    # 保存文件
    file_path = UPLOAD_DIR / safe_name

    content = await file.read()
    file_path.write_bytes(content)

    # 解析与切片
    text = read_file(file_path)  # 复用 Day 2 的 read_file
    chunks = chunk_text(text, chunk_size=500, overlap=50)

    # 向量化存入
    ids, embeddings = [], []
    for chunk in chunks:
        chunk_id = str(uuid.uuid4())
        embedding = model.encode([chunk]).tolist()[0]
        ids.append(chunk_id)
        embeddings.append(embedding)

    collection.add(
        ids=ids, documents=chunks, embeddings=embeddings,
        metadatas=[{"source": file.filename}] * len(chunks)
    )
    return {"message": f"文件 {file.filename} 上传成功，共 {len(chunks)} 个片段已入库"}


@router.post("/ask")
async def ask_question(
        question: str,
        token: str = Depends(verify_token)
):
    """非流式 RAG 问答"""
    return await rag_ask(question)


@router.post("/ask/stream")
async def ask_question_stream(
        question: str,
        token: str = Depends(verify_token)
):
    """流式 RAG 问答，SSE 格式"""

    async def event_stream():
        async for chunk in rag_ask_stream(question):
            yield f"data: {chunk}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
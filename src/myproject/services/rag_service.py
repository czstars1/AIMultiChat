import json
import os
from pathlib import Path

import httpx
from chromadb import PersistentClient
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

base_dir = Path(__file__).resolve().parent
db_path = base_dir / "data" / "chroma_db"
env_file = base_dir / ".env"

client = PersistentClient(path=str(db_path))
collection = client.get_collection(name="knowledge_base")
model = SentenceTransformer('all-MiniLM-L6-v2')

load_dotenv(dotenv_path=env_file)
OLLAMA_CHAT_API = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
MODEL_NAME=os.getenv("MODEL_NAME","qwen2.5:7b")

def retrieve_docs(question: str,n_docs: int = 3):
    question_emb = model.encode([question]).tolist()
    results = collection.query(query_embeddings=question_emb,n_results=n_docs)
    docs = results['documents'][0] if results['documents'] else []
    sources = [meta['source'] for meta in results['metadatas'][0]] if results['metadatas'] else []
    return docs, sources

def build_prompt(question: str, docs: list):
    """构造 RAG 提示词，返回 Ollama 需要的 messages 格式"""
    context = "\n\n".join([f"[参考资料{i+1}] {doc}" for i, doc in enumerate(docs)])
    system_prompt = (
        "你是一个基于内部知识库的智能问答助手。"
        "请严格根据以下参考资料回答用户的问题。"
        "如果资料中没有相关信息，请直接回答'知识库中没有找到相关信息'，不要编造。"
    )
    user_prompt = f"{context}\n\n用户问题：{question}\n请基于以上资料回答。"
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]


async def rag_ask(question: str, n_docs: int = 3) -> dict:
    """非流式 RAG 问答"""
    docs, sources = retrieve_docs(question, n_docs)
    if not docs:
        return {"answer": "抱歉，没有在知识库中找到与您问题相关的资料。", "sources": []}

    messages = build_prompt(question, docs)
    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {"model": MODEL_NAME, "messages": messages, "stream": False, "keep_alive": -1}
        response = await client.post(OLLAMA_CHAT_API, json=payload)
        response.raise_for_status()
        data = response.json()
    return {"answer": data["message"]["content"], "sources": sources}


async def rag_ask_stream(question: str, n_docs: int = 3):
    """流式 RAG 问答，逐词 yield，最后 yield '__SOURCES__:...'"""
    docs, sources = retrieve_docs(question, n_docs)
    if not docs:
        yield "抱歉，没有在知识库中找到与您问题相关的资料。"
        yield "__SOURCES__:[]"
        return

    messages = build_prompt(question, docs)
    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {"model": MODEL_NAME, "messages": messages, "stream": True, "keep_alive": -1}
        async with client.stream("POST", OLLAMA_CHAT_API, json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if "message" in data and "content" in data["message"]:
                        yield data["message"]["content"]
                    if data.get("done"):
                        break
                except json.JSONDecodeError:
                    continue
    yield "__SOURCES__:" + json.dumps(sources)

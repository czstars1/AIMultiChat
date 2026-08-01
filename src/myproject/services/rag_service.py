import asyncio
import hashlib
import json
import re
from pathlib import Path

import httpx
from sentence_transformers import CrossEncoder
from src.myproject.deps import model, collection
from src.myproject.services import llm_service
from src.myproject.config import OLLAMA_CHAT_API, MODEL_NAME
# 1. 答案缓存字典
answer_cache = {}

# 2. 重排序模型（懒加载，首次调用时下载，约 80MB）
_reranker = None

def get_reranker():
    global _reranker
    if _reranker is None:
        # 轻量级且效果很好的重排模型
        _reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    return _reranker


def retrieve_docs(question: str, n_docs: int = 3) -> tuple:
    """
    向量检索 + 重排序（Re-rank）
    1. 先从向量库取 top_initial=10 篇
    2. 用 CrossEncoder 重排序，取最相关的 top_k=n_docs
    """
    # 1. 获取原始查询向量
    question_emb = model.encode([question]).tolist()

    # 2. 先多取一点候选（比如10篇），给重排序留出筛选空间
    initial_k = 10
    results = collection.query(
        query_embeddings=question_emb,
        n_results=initial_k
    )

    # 提取文档和来源（未排序前）
    raw_docs = results['documents'][0] if results['documents'] else []
    raw_sources = [meta.get('source', '未知来源') for meta in results['metadatas'][0]] if results['metadatas'] else []

    if not raw_docs:
        return [], []

    # 3. 如果候选数量小于等于目标数，直接返回
    if len(raw_docs) <= n_docs:
        return raw_docs, raw_sources
    print(f"重排前 Top3: {raw_docs[:3]}")
    # 4. ⭐ 重排序核心逻辑
    reranker = get_reranker()
    # 构建 (问题, 文档) 对
    pairs = [[question, doc] for doc in raw_docs]
    # 预测相关性分数（分数越高越相关）
    scores = reranker.predict(pairs)

    # 5. 按照分数从高到低排序
    ranked_pairs = sorted(zip(raw_docs, raw_sources, scores), key=lambda x: x[2], reverse=True)

    # 6. 取前 n_docs 个返回
    final_docs = [item[0] for item in ranked_pairs[:n_docs]]
    final_sources = [item[1] for item in ranked_pairs[:n_docs]]

    print(f"🔄 重排序完成: 从 {initial_k} 个候选中选出最相关的 {len(final_docs)} 个")
    return final_docs, final_sources

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


async def rewrite_query(original_question: str) -> str:
    """用 LLM 将口语化问题改写为关键词检索形式（开销极小）"""
    prompt = f"""请将以下用户问题改写为更简洁、更适合在文档中检索的关键词形式，只输出改写后的内容，不要解释。

用户问题：{original_question}"""

    messages = [{"role": "user", "content": prompt}]
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(OLLAMA_CHAT_API, json={
                "model": MODEL_NAME,  # 复用你的主模型
                "messages": messages,
                "stream": False,
                "keep_alive": -1
            })
            rewritten = response.json()["message"]["content"].strip()
            print(f"✏️ 查询重写: {original_question} -> {rewritten}")
            return rewritten
    except Exception as e:
        print(f"⚠️ 查询重写失败，使用原始问题: {e}")
        return original_question


async def rag_ask(question: str, n_docs: int = 3) -> dict:
    """非流式 RAG 问答（集成 查询重写 + 缓存）"""

    # ===== 1. 缓存检查 =====
    # 标准化 key（忽略大小写和首尾空格）
    cache_key = hashlib.md5(question.strip().lower().encode()).hexdigest()
    if cache_key in answer_cache:
        print(f"✅ 命中缓存，直接返回答案")
        return answer_cache[cache_key]

    # ===== 2. 查询重写 =====
    rewritten_q = await rewrite_query(question)

    # ===== 3. 检索 + 重排（retrieve_docs 已内置重排） =====
    docs, sources = retrieve_docs(rewritten_q, n_docs)
    if not docs:
        result = {"answer": "抱歉，没有在知识库中找到与您问题相关的资料。", "sources": []}
        answer_cache[cache_key] = result
        return result

    # ===== 4. 调用 LLM =====
    messages = build_prompt(question, docs)  # 注意：prompt 用原始问题还是改写问题？建议用原始问题，因为用户问得自然

    answer = await llm_service.call_llm(messages)
    result = {"answer": answer, "sources": sources}

    # ===== 5. 存入缓存 =====
    answer_cache[cache_key] = result
    print(f"💾 答案已缓存 (当前缓存大小: {len(answer_cache)})")

    return result


async def rag_ask_stream(question: str, n_docs: int = 3):
    """流式 RAG（缓存 + 调用 stream_llm）"""
    cache_key = hashlib.md5(question.strip().lower().encode()).hexdigest()

    # ===== 1. 缓存命中：按句子输出 =====
    if cache_key in answer_cache:
        print(f"✅ 流式命中缓存")
        cached_answer = answer_cache[cache_key]["answer"]
        # 按句子切割（保留标点）
        sentences = re.split(r'(?<=[。！？.!?])', cached_answer)
        for sentence in sentences:
            if sentence.strip():
                yield sentence  # 由上层路由包装成 SSE
                await asyncio.sleep(0.03)
        # 输出来源
        sources = answer_cache[cache_key]["sources"]
        if sources:
            yield f"__SOURCES__:{json.dumps(sources)}"
        yield "[DONE]"
        return

    # ===== 2. 未命中：查询重写 + 检索 + 重排 =====
    rewritten_q = await rewrite_query(question)
    docs, sources = retrieve_docs(rewritten_q, n_docs)

    if not docs:
        error_msg = "抱歉，没有在知识库中找到与您问题相关的资料。"
        yield error_msg
        yield "[DONE]"
        return

    # ===== 3. 构建 Prompt =====
    messages = build_prompt(question, docs)

    # ===== 4. 调用流式 LLM（复用 llm_service.stream_llm） =====
    full_answer = ""
    try:
        async for chunk in llm_service.stream_llm(messages):
            if chunk:
                full_answer += chunk
                yield chunk  # 直接产出内容块
    except Exception as e:
        error_msg = f"⚠️ LLM 调用失败: {str(e)}"
        yield error_msg
        yield "[DONE]"
        return

    # ===== 5. 缓存完整答案 =====
    if full_answer:
        result = {"answer": full_answer, "sources": sources}
        answer_cache[cache_key] = result
        print(f"💾 流式结果已缓存 (长度: {len(full_answer)})")

    # ===== 6. 输出来源和结束符 =====
    if sources:
        yield f"__SOURCES__:{json.dumps(sources)}"
    yield "[DONE]"
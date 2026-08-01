import os
import uuid
from pathlib import Path
import pdfplumber

from docx import Document
from src.myproject.deps import model,collection

def index_file(file_path: str, chunk_size: int = 500,overlap: int = 50):
    """处理文件，切片后存入向量数据库"""
    print(f"正在处理: {file_path}")

    full_text = read_file(file_path)
    if not full_text.strip():
        print(f"警告：{file_path} 内容为空或无法提取文本，跳过")
        return

    chunks = chunk_text(full_text, chunk_size, overlap)
    print(f"  切分成 {len(chunks)} 个片段")

    ids = []
    documents = []
    embeddings = []
    metadatas = []

    for i,chunk in enumerate(chunks):
        chunk_id = str(uuid.uuid4())

        emb = model.encode([chunk],show_progress_bar=False).tolist()[0]

        ids.append(chunk_id)
        documents.append(chunk)
        embeddings.append(emb)
        metadatas.append({
            "source": os.path.basename(file_path),
            "chunk_index": i,
        })

    if ids:
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        print(f"  已存入 {len(ids)} 个片段到集合 'knowledge_base'")


def read_file(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.txt':
        with open(file_path,"r",encoding="utf-8")as f:
            return f.read()
    elif ext == '.pdf':
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return '\n'.join(text_parts)
    elif ext == '.doc':
        doc = Document(file_path)
        return '\n'.join([pare.text for pare in doc.paragraphs])
    else:
        raise ValueError(f"不支持的文件类型：{ext}")

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start = 0
    text_len = len(text)

    if text_len <= chunk_size:
        return [text]

    while start < text_len:
        end = start + chunk_size

        chunk = text[start:end]
        chunks.append(chunk)

        start = end - overlap

        if start >= text_len:
            break
    return chunks
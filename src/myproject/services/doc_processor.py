


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
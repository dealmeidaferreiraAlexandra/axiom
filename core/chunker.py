# core/chunker.py

def chunk_text(text, chunk_size=500, overlap=100):
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    step = chunk_size - overlap
    if step <= 0:
        step = chunk_size

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += step

    return chunks
# core/search.py

from core.embedder import embed_texts

def search(query, indexer, k=5):
    query_embedding = embed_texts([query])[0]
    return indexer.search(query_embedding, k=k)
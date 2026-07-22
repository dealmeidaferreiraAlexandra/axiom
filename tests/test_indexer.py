import numpy as np

from core.embedder import EMBEDDING_DIM, embed_texts
from core.indexer import Indexer


def test_new_indexer_is_empty():
    indexer = Indexer(EMBEDDING_DIM)
    assert indexer.texts == []
    assert indexer.index.ntotal == 0


def test_add_stores_texts_and_vectors():
    texts = ["alpha", "beta", "gamma"]
    embeddings = embed_texts(texts)
    indexer = Indexer(EMBEDDING_DIM)
    indexer.add(embeddings, texts)
    assert indexer.texts == texts
    assert indexer.index.ntotal == 3


def test_search_returns_most_similar_text_first():
    texts = [
        "machine learning and neural networks",
        "cooking pasta with tomato sauce",
        "hiking trails in the mountains",
    ]
    embeddings = embed_texts(texts)
    indexer = Indexer(EMBEDDING_DIM)
    indexer.add(embeddings, texts)

    query = embed_texts(["deep learning neural networks"])[0]
    results = indexer.search(query, k=3)
    assert results[0] == "machine learning and neural networks"


def test_search_respects_k():
    texts = [f"document number {i}" for i in range(5)]
    embeddings = embed_texts(texts)
    indexer = Indexer(EMBEDDING_DIM)
    indexer.add(embeddings, texts)

    query = embed_texts(["document number 2"])[0]
    results = indexer.search(query, k=2)
    assert len(results) == 2


def test_search_when_k_exceeds_stored_items_filters_missing():
    texts = ["only one document"]
    embeddings = embed_texts(texts)
    indexer = Indexer(EMBEDDING_DIM)
    indexer.add(embeddings, texts)

    query = embed_texts(["only one document"])[0]
    results = indexer.search(query, k=5)
    # faiss pads missing neighbours with index -1, which must be filtered out.
    assert results == ["only one document"]


def test_add_accepts_list_input():
    texts = ["list based embeddings"]
    embeddings = embed_texts(texts).tolist()
    indexer = Indexer(EMBEDDING_DIM)
    indexer.add(embeddings, texts)
    assert indexer.index.ntotal == 1
    query = np.array(embeddings[0], dtype="float32")
    assert indexer.search(query, k=1) == texts

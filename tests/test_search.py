from core.embedder import EMBEDDING_DIM, embed_texts
from core.indexer import Indexer
from core.search import search


def _build_indexer(texts):
    indexer = Indexer(EMBEDDING_DIM)
    indexer.add(embed_texts(texts), texts)
    return indexer


def test_search_returns_relevant_text():
    texts = [
        "the history of ancient rome",
        "introduction to python programming",
        "recipes for chocolate cake",
    ]
    indexer = _build_indexer(texts)
    results = search("python programming tutorial", indexer, k=3)
    assert results[0] == "introduction to python programming"


def test_search_respects_k():
    texts = [f"topic {i}" for i in range(4)]
    indexer = _build_indexer(texts)
    results = search("topic 1", indexer, k=2)
    assert len(results) == 2


def test_search_default_k():
    texts = [f"entry {i}" for i in range(10)]
    indexer = _build_indexer(texts)
    results = search("entry 3", indexer)
    # default k is 5
    assert len(results) == 5

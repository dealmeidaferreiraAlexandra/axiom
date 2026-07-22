import numpy as np

from core.embedder import EMBEDDING_DIM, embed_texts


def test_empty_input_returns_empty_array():
    result = embed_texts([])
    assert isinstance(result, np.ndarray)
    assert result.size == 0


def test_output_shape_and_dtype():
    texts = ["hello world", "another document"]
    embeddings = embed_texts(texts)
    assert embeddings.shape == (2, EMBEDDING_DIM)
    assert embeddings.dtype == np.dtype("float32")


def test_embeddings_are_unit_normalized():
    embeddings = embed_texts(["semantic search over files"])
    norm = np.linalg.norm(embeddings[0])
    assert np.isclose(norm, 1.0, atol=1e-5)


def test_embedding_is_deterministic():
    a = embed_texts(["repeatable content here"])
    b = embed_texts(["repeatable content here"])
    assert np.array_equal(a, b)


def test_case_insensitive():
    lower = embed_texts(["Hello World"])
    upper = embed_texts(["HELLO WORLD"])
    assert np.array_equal(lower, upper)


def test_text_without_terms_yields_zero_vector():
    # Only punctuation/whitespace -> no terms matched -> zero vector (norm 0).
    embeddings = embed_texts(["... !!! ---"])
    assert embeddings.shape == (1, EMBEDDING_DIM)
    assert np.linalg.norm(embeddings[0]) == 0.0


def test_different_texts_produce_different_embeddings():
    a = embed_texts(["cats and dogs"])
    b = embed_texts(["quantum physics lecture"])
    assert not np.array_equal(a, b)

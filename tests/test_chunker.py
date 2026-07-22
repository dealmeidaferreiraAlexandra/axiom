from core.chunker import chunk_text


def test_empty_text_returns_no_chunks():
    assert chunk_text("") == []


def test_text_shorter_than_chunk_size_returns_single_chunk():
    text = "hello world"
    chunks = chunk_text(text, chunk_size=500, overlap=100)
    assert chunks == [text]


def test_chunks_reconstruct_and_respect_size():
    text = "abcdefghij"  # length 10
    chunks = chunk_text(text, chunk_size=4, overlap=0)
    # step == chunk_size == 4 -> non-overlapping slices
    assert chunks == ["abcd", "efgh", "ij"]
    assert "".join(chunks) == text


def test_overlap_repeats_tail_of_previous_chunk():
    text = "abcdefghij"  # length 10
    chunks = chunk_text(text, chunk_size=5, overlap=2)
    # step == 5 - 2 == 3
    assert chunks[0] == "abcde"
    assert chunks[1] == "defgh"  # overlaps last 2 chars of chunk 0
    assert chunks[1].startswith(chunks[0][-2:])


def test_every_chunk_within_chunk_size():
    text = "x" * 1234
    chunk_size = 100
    chunks = chunk_text(text, chunk_size=chunk_size, overlap=20)
    assert all(len(c) <= chunk_size for c in chunks)
    assert chunks  # non-empty


def test_default_arguments():
    text = "y" * 1000
    chunks = chunk_text(text)
    # defaults: chunk_size=500, overlap=100 -> step 400
    assert chunks[0] == "y" * 500
    assert len(chunks) >= 2

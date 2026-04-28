# core/embedder.py

import hashlib
import re

import numpy as np


EMBEDDING_DIM = 384


def embed_texts(texts, batch_size=1):
    if not texts:
        return np.array([])

    embeddings = np.zeros((len(texts), EMBEDDING_DIM), dtype="float32")

    for row, text in enumerate(texts):
        terms = re.findall(r"[A-Za-zÀ-ÿ0-9_]+", text.lower())

        for term in terms:
            digest = hashlib.md5(term.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "little") % EMBEDDING_DIM
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            embeddings[row, idx] += sign

        norm = np.linalg.norm(embeddings[row])
        if norm > 0:
            embeddings[row] /= norm

    return embeddings

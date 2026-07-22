# developed by Alexandra de Almeida Ferreira
# Search pipeline shared by the local and cloud apps (no Streamlit dependency).

import os

import numpy as np

import config
from core.loader import load_file_pages
from core.chunker import chunk_text
from core.embedder import embed_texts
from core.indexer import Indexer
from utils.helpers import (
    get_logger,
    chunk_matches_query,
    extract_search_units,
    ranked_indices_by_pdf,
    relevance_from_distance,
    relevance_color,
    display_source_with_page,
    build_snippet,
    highlight_snippet,
    explain_match,
)

logger = get_logger(__name__)


def collect_chunks(root_path: str, query: str):
    """Scan ``root_path`` and return chunks matching ``query``.

    Falls back to the first chunks found when nothing matches the query.
    Returns a tuple ``(chunks, sources, pages, skipped_files)`` where
    ``skipped_files`` counts files that could not be read.
    """
    all_chunks = []
    chunk_sources = []
    chunk_pages = []
    fallback_chunks = []
    fallback_sources = []
    fallback_pages = []
    source_chunk_counts = {}
    skipped_files = 0

    for root_dir, dirs, files in os.walk(root_path):
        for filename in files:
            path = os.path.join(root_dir, filename)

            if not filename.lower().endswith(config.SUPPORTED_EXTENSIONS):
                continue

            try:
                file_pages = load_file_pages(path)
            except Exception as e:
                skipped_files += 1
                logger.warning("Skipping unreadable file %s: %s", path, e)
                continue

            for page_number, text in file_pages:
                chunks = chunk_text(text)

                for chunk in chunks:
                    if not chunk.strip():
                        continue

                    if len(fallback_chunks) < config.MAX_FALLBACK_CHUNKS:
                        fallback_chunks.append(chunk)
                        fallback_sources.append(path)
                        fallback_pages.append(page_number)

                    if source_chunk_counts.get(path, 0) >= config.MAX_CHUNKS_PER_FILE:
                        continue

                    if chunk_matches_query(chunk, query):
                        all_chunks.append(chunk)
                        chunk_sources.append(path)
                        chunk_pages.append(page_number)
                        source_chunk_counts[path] = source_chunk_counts.get(path, 0) + 1

                    if len(all_chunks) >= config.MAX_CHUNKS:
                        break

                if len(all_chunks) >= config.MAX_CHUNKS:
                    break

            if len(all_chunks) >= config.MAX_CHUNKS:
                break

        if len(all_chunks) >= config.MAX_CHUNKS:
            break

    if len(all_chunks) == 0:
        return fallback_chunks, fallback_sources, fallback_pages, skipped_files

    return all_chunks, chunk_sources, chunk_pages, skipped_files


def build_index(all_chunks):
    """Embed ``all_chunks`` and build a FAISS index.

    Returns ``(indexer, embeddings)`` or ``(None, [])`` when embedding fails.
    """
    embeddings = embed_texts(all_chunks)
    if len(embeddings) == 0:
        return None, embeddings

    indexer = Indexer(len(embeddings[0]))
    indexer.add(embeddings, all_chunks)
    return indexer, embeddings


def search(indexer, all_chunks, sources, query):
    """Query the index and return ranked ``(idx, distance)`` candidates."""
    search_units = extract_search_units(query)
    query_embeddings = embed_texts([query] + search_units)
    top_k = min(max(30, len(search_units) * 10), len(all_chunks))

    distances, indices = indexer.index.search(
        np.array(query_embeddings).astype("float32"),
        top_k
    )

    return ranked_indices_by_pdf(
        indices.flatten(),
        distances.flatten(),
        sources,
        max_results=config.MAX_RESULTS,
        min_pdf_files=config.MIN_PDF_FILES,
    )


def format_results(ranked_results, chunks, sources, pages, root_path, query):
    """Turn ranked candidates into display-ready result dictionaries."""
    results = []

    for rank, (idx, dist) in enumerate(ranked_results, start=1):
        chunk_text_value = chunks[idx]
        source = sources[idx]
        page_number = pages[idx] if idx < len(pages) else None
        display_path = display_source_with_page(source, root_path, page_number)
        relevance = relevance_from_distance(dist)

        snippet = build_snippet(chunk_text_value, query, max_len=320)
        highlighted = highlight_snippet(snippet, query)
        explanation = explain_match(chunk_text_value, query)

        results.append(
            {
                "rank": rank,
                "idx": idx,
                "source": source,
                "display_path": display_path,
                "relevance": relevance,
                "relevance_color": relevance_color(relevance),
                "explanation": explanation,
                "highlighted": highlighted,
            }
        )

    return results

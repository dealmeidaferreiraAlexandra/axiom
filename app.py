# developed by Alexandra de Almeida Ferreira

import os
import re
import html
import sys
import subprocess
import math

import numpy as np
import streamlit as st

from core.loader import load_file_pages
from core.chunker import chunk_text
from core.embedder import embed_texts
from core.indexer import Indexer

try:
    from tkinter import Tk, filedialog
    TK_AVAILABLE = True
except Exception:
    TK_AVAILABLE = False


st.set_page_config(page_title="AXIOM — SEEKR mode", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background:#020617; color:#e2e8f0; }

    .left-panel {
        border-right:1px solid #1f2231;
        padding-right:12px;
        min-height: auto !important;
    }

    .right-panel {
        background:#050a18;
        padding:20px;
        border-radius:16px;
        min-height: auto !important;
    }

    .stTextInput>div>div>input {
        background:#020617;
        color:#e2e8f0;
        border:1px solid #1f2231;
    }

    .stButton>button {
        width:100%;
        background:linear-gradient(90deg,#6366f1,#8b5cf6);
        border-radius:10px;
        transition: all 0.25s ease;
        border: none;
        color: white;
    }

    .stButton>button:hover {
        box-shadow:0 0 20px rgba(139,92,246,0.8);
    }

    .st-key-reset_root_scope button,
    .st-key-reset_search_results button,
    div[data-testid="stButton"][data-st-key="reset_root_scope"] button,
    div[data-testid="stButton"][data-st-key="reset_search_results"] button {
        background:linear-gradient(90deg,#dc2626,#ef4444);
    }

    .st-key-reset_root_scope button:hover,
    .st-key-reset_search_results button:hover,
    div[data-testid="stButton"][data-st-key="reset_root_scope"] button:hover,
    div[data-testid="stButton"][data-st-key="reset_search_results"] button:hover {
        box-shadow:0 0 20px rgba(239,68,68,0.8);
    }

    .st-key-reset_search_results {
        display:flex;
        align-items:center;
        height:100%;
    }

    .st-key-reset_search_results button {
        margin-top:6px;
    }

    div[data-testid="stButton"][data-st-key="reset_search_results"] {
        margin-top:8px;
    }

    .card {
        border:1px solid #1f2231;
        border-radius:14px;
        padding:16px;
        margin-top:16px;
        background:#020617;
    }

    .pipe {
        border:1px solid #1f2231;
        border-radius:12px;
        padding:12px;
        text-align:center;
        margin-bottom:10px;
        background:#020617;
    }

    .active {
        border:1px solid #6366f1;
        box-shadow:0 0 20px rgba(99,102,241,0.6);
    }

    .footer {
        text-align:center;
        opacity:0.6;
        margin-top:40px;
        padding-top:16px;
        border-top:1px solid #1f2231;
    }

    .block-container {
        padding-top: 2rem;
    }

    mark {
        background: rgba(139, 92, 246, 0.35);
        color: #e2e8f0;
        padding: 0 4px;
        border-radius: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("AXIOM")
st.caption("SEEKR mode — Search your system intelligently")
st.markdown("---")


def pick_folder():
    if sys.platform == "darwin":
        try:
            result = subprocess.run(
                ["osascript", "-e", 'POSIX path of (choose folder with prompt "Select root folder")'],
                capture_output=True,
                text=True,
                check=False
            )
            folder = result.stdout.strip()
            return folder if folder else None
        except Exception:
            return None

    if not TK_AVAILABLE:
        return None

    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    folder = filedialog.askdirectory(title="Select root folder")
    root.destroy()
    return folder if folder else None


def reset_search_state(clear_query=False):
    if clear_query:
        st.session_state.query = ""

    st.session_state.indexer = None
    st.session_state.sources = []
    st.session_state.chunks = []
    st.session_state.pages = []
    st.session_state.search_results = []
    st.session_state.stage = "input"


def open_file_in_os(path: str) -> bool:
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception:
        return False


def extract_terms(query: str) -> list[str]:
    terms = re.findall(r"[A-Za-zÀ-ÿ0-9_]+", query)
    return [t for t in terms if len(t) > 2]


def extract_search_units(query: str) -> list[str]:
    units = [unit.strip() for unit in query.split(",") if unit.strip()]
    units = units if units else [query.strip()]
    return units[:5]


def chunk_matches_query(text: str, query: str) -> bool:
    lower_text = text.lower()

    for unit in extract_search_units(query):
        lower_unit = unit.lower()
        if lower_unit and lower_unit in lower_text:
            return True

        for term in extract_terms(unit):
            if term.lower() in lower_text:
                return True

    return False


def build_snippet(text: str, query: str, max_len: int = 320) -> str:
    clean_text = re.sub(r"\s+", " ", text).strip()
    terms = extract_terms(query)

    if not clean_text:
        return ""

    if not terms:
        return clean_text[:max_len] + ("..." if len(clean_text) > max_len else "")

    lower_text = clean_text.lower()
    first_pos = None

    for term in terms:
        pos = lower_text.find(term.lower())
        if pos != -1:
            if first_pos is None or pos < first_pos:
                first_pos = pos

    if first_pos is None:
        snippet = clean_text[:max_len]
        if len(clean_text) > max_len:
            snippet += "..."
        return snippet

    start = max(0, first_pos - max_len // 3)
    end = min(len(clean_text), start + max_len)

    snippet = clean_text[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(clean_text):
        snippet = snippet + "..."

    return snippet


def highlight_snippet(snippet: str, query: str) -> str:
    escaped = html.escape(snippet)
    terms = extract_terms(query)

    for term in sorted(set(terms), key=len, reverse=True):
        pattern = re.compile(re.escape(html.escape(term)), re.IGNORECASE)
        escaped = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", escaped)

    return escaped


def explain_match(text: str, query: str) -> str:
    lower_text = text.lower()
    matched_terms = []

    for term in extract_terms(query):
        if term.lower() in lower_text and term not in matched_terms:
            matched_terms.append(term)

    if matched_terms:
        return "Este ficheiro apareceu porque contém " + ", ".join(matched_terms) + "."

    return "Este ficheiro apareceu porque contém conteúdo semanticamente relacionado com a pesquisa."


def relevance_from_distance(distance: float) -> float:
    distance = float(distance)
    if not math.isfinite(distance):
        return 0.0

    return max(0.0, 100.0 / (1.0 + distance))


def display_source_path(source: str, root_path: str) -> str:
    root_name = os.path.basename(os.path.normpath(root_path))
    try:
        relative_path = os.path.relpath(source, root_path)
    except ValueError:
        return source

    if relative_path == ".":
        return root_name

    return os.path.join(root_name, relative_path)


def display_source_with_page(source: str, root_path: str, page_number) -> str:
    display_path = display_source_path(source, root_path)

    if page_number is None:
        return display_path

    return f"{display_path} | page {page_number}"


def ranked_indices_by_pdf(indices, distances, sources, max_results=7, min_pdf_files=3):
    candidates = {}

    for idx, dist in zip(indices, distances):
        idx = int(idx)
        if idx == -1 or idx >= len(sources):
            continue

        dist = float(dist)
        if not math.isfinite(dist):
            continue

        if idx not in candidates or dist < candidates[idx]:
            candidates[idx] = dist

    sorted_candidates = sorted(candidates.items(), key=lambda item: item[1])
    selected = []
    selected_set = set()
    selected_pdfs = set()

    for idx, dist in sorted_candidates:
        source = sources[idx]
        if not source.lower().endswith(".pdf") or source in selected_pdfs:
            continue

        selected.append((idx, dist))
        selected_set.add(idx)
        selected_pdfs.add(source)

        if len(selected_pdfs) >= min_pdf_files or len(selected) >= max_results:
            break

    for idx, dist in sorted_candidates:
        if idx in selected_set:
            continue

        selected.append((idx, dist))
        selected_set.add(idx)

        if len(selected) >= max_results:
            break

    return selected


if "root_path" not in st.session_state:
    st.session_state.root_path = ""

if "indexer" not in st.session_state:
    st.session_state.indexer = None

if "sources" not in st.session_state:
    st.session_state.sources = []

if "chunks" not in st.session_state:
    st.session_state.chunks = []

if "pages" not in st.session_state:
    st.session_state.pages = []

if "query" not in st.session_state:
    st.session_state.query = ""

if "stage" not in st.session_state:
    st.session_state.stage = "input"

if "search_results" not in st.session_state:
    st.session_state.search_results = []


left, right = st.columns([0.3, 0.7])

with left:
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)

    st.subheader("📂 Data Scope")

    st.session_state.root_path = st.text_input(
        "Root directory",
        value=st.session_state.root_path,
        placeholder="/Users/yourname/Documents"
    )

    c1, c2, c3 = st.columns([0.30, 0.22, 0.48])
    with c1:
        browse_clicked = st.button(
            "📁 Browse"
        )
        if not TK_AVAILABLE and sys.platform != "darwin":
            st.caption("Folder picker not supported on this system. Please paste the path.")
    with c2:
        clear_clicked = st.button("Reset", key="reset_root_scope")

    if browse_clicked:
        try:
            folder = pick_folder()
            if folder:
                st.session_state.root_path = folder
                reset_search_state(clear_query=False)
                st.rerun()
        except Exception as e:
            st.error("Folder picker failed on this system.")

    if clear_clicked:
        st.session_state.root_path = ""
        reset_search_state(clear_query=True)
        st.rerun()

    st.markdown("### 🔍 Query")
    st.session_state.query = st.text_input(
        "Search",
        value=st.session_state.query,
        placeholder="e.g. deep learning notes"
    )
    st.caption("Independent words and comma-separated phrases.")

    MIN_QUERY_LENGTH = 5

    run = st.button("🚀 SEEKR")

    st.markdown("### System Status")
    if st.session_state.root_path:
        st.write("🟢 Path defined")
        st.code(st.session_state.root_path, language="text")
    else:
        st.write("🟡 Waiting path")

    if st.session_state.indexer is not None:
        st.write(f"🟢 Indexed chunks: {len(st.session_state.chunks)}")
    else:
        st.write("🟡 No index created yet")

    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)

    pipeline_placeholder = st.empty()
    discovery_placeholder = st.empty()

    def pipe(col, icon, title, desc, key):
        active = st.session_state.stage == key
        with col:
            st.markdown(
                f"""
                <div class="pipe {'active' if active else ''}">
                {icon}<br>
                <b>{title}</b><br>
                <span style="opacity:0.6;font-size:11px;">{desc}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

    def render_pipeline():
        with pipeline_placeholder.container():
            p1, p2, p3, p4 = st.columns(4)
            pipe(p1, "📥", "INPUT", "Define scope", "input")
            pipe(p2, "📂", "SCAN", "Read files", "scan")
            pipe(p3, "🧠", "EMBED", "Vectorize", "embed")
            pipe(p4, "📊", "RESULT", "Show results", "result")

    def render_results():
        c_results_title, c_results_reset = st.columns([0.82, 0.18], vertical_alignment="center")
        with c_results_title:
            st.markdown("## 📊 Results")
        with c_results_reset:
            if st.button("Reset search", key="reset_search_results"):
                reset_search_state(clear_query=True)
                st.rerun()

        for result in st.session_state.search_results:
            if not all(key in result for key in ("rank", "idx", "source", "display_path", "relevance", "relevance_color", "explanation", "highlighted")):
                continue

            try:
                with st.container(border=True):
                    c_title, c_open = st.columns([0.82, 0.18])
                    with c_title:
                        st.markdown(
                            f"""
                            <div><b>#{result["rank"]} 📄 {html.escape(str(result["display_path"]))}</b></div>
                            <div style="margin-top:6px;color:{result["relevance_color"]};">
                                Relevance: {float(result["relevance"]):.1f}%
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    with c_open:
                        if st.button("Open file", key=f"open_{result['rank']}_{result['idx']}"):
                            if not open_file_in_os(result["source"]):
                                st.error("Could not open the file on this system.")
                    st.markdown(
                        f"""
                        <div style="margin-top:12px;line-height:1.6;">
                            {html.escape(str(result["explanation"]))}
                        </div>
                        <div style="margin-top:12px;line-height:1.6;">
                            {result["highlighted"]}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            except Exception:
                continue

    def render_start_card(loading=False):
        loading_html = ""
        if loading:
            loading_html = '<div style="display:flex;gap:8px;margin-top:14px;"><span style="width:8px;height:8px;border-radius:999px;background:#8b5cf6;display:inline-block;"></span><span style="width:8px;height:8px;border-radius:999px;background:#8b5cf6;display:inline-block;opacity:0.65;"></span><span style="width:8px;height:8px;border-radius:999px;background:#8b5cf6;display:inline-block;opacity:0.35;"></span></div>'

        discovery_placeholder.markdown(
            f"""
            <div class="card">
                <h3>🧠 Start</h3>
                Intelligent File Discovery
                Search across your local data using semantic AI.
                {loading_html}
            </div>
            """,
            unsafe_allow_html=True
        )

    render_pipeline()

    discovery_card_rendered = False

    if run:
        root_path = st.session_state.root_path.strip()
        query = st.session_state.query.strip()

        if not root_path:
            st.session_state.stage = "input"
            st.session_state.search_results = []
            render_pipeline()
            st.warning("Please define a root directory.")

        elif not os.path.exists(root_path):
            st.session_state.stage = "input"
            st.session_state.search_results = []
            render_pipeline()
            st.error("Invalid directory.")

        elif not query or len(query) < MIN_QUERY_LENGTH:
            st.session_state.stage = "input"
            st.session_state.search_results = []
            render_pipeline()
            st.warning(f"Query must have at least {MIN_QUERY_LENGTH} characters.")

        else:
            render_start_card(loading=True)

            all_chunks = []
            chunk_sources = []
            chunk_pages = []
            fallback_chunks = []
            fallback_sources = []
            fallback_pages = []
            source_chunk_counts = {}
            max_chunks = 300
            max_fallback_chunks = 120
            max_chunks_per_file = 80

            st.session_state.stage = "scan"
            render_pipeline()

            with st.spinner("Scanning files..."):
                for root_dir, dirs, files in os.walk(root_path):
                    for filename in files:
                        path = os.path.join(root_dir, filename)

                        if not filename.lower().endswith((".txt", ".pdf", ".docx")):
                            continue

                        try:
                            file_pages = load_file_pages(path)
                        except Exception:
                            continue

                        for page_number, text in file_pages:
                            chunks = chunk_text(text)

                            for chunk in chunks:
                                if not chunk.strip():
                                    continue

                                if len(fallback_chunks) < max_fallback_chunks:
                                    fallback_chunks.append(chunk)
                                    fallback_sources.append(path)
                                    fallback_pages.append(page_number)

                                if source_chunk_counts.get(path, 0) >= max_chunks_per_file:
                                    continue

                                if chunk_matches_query(chunk, query):
                                    all_chunks.append(chunk)
                                    chunk_sources.append(path)
                                    chunk_pages.append(page_number)
                                    source_chunk_counts[path] = source_chunk_counts.get(path, 0) + 1

                                if len(all_chunks) >= max_chunks:
                                    break

                            if len(all_chunks) >= max_chunks:
                                break

                        if len(all_chunks) >= max_chunks:
                            break

                    if len(all_chunks) >= max_chunks:
                        break

            if len(all_chunks) == 0:
                all_chunks = fallback_chunks
                chunk_sources = fallback_sources
                chunk_pages = fallback_pages

            if len(all_chunks) == 0:
                st.session_state.stage = "input"
                st.session_state.search_results = []
                render_pipeline()
                st.warning("No readable files found.")

            else:
                st.session_state.stage = "embed"
                render_pipeline()

                embeddings = embed_texts(all_chunks)

                if len(embeddings) == 0:
                    st.session_state.stage = "input"
                    st.session_state.search_results = []
                    render_pipeline()
                    st.error("Embedding generation failed.")

                else:
                    indexer = Indexer(len(embeddings[0]))
                    indexer.add(embeddings, all_chunks)

                    st.session_state.indexer = indexer
                    st.session_state.sources = chunk_sources
                    st.session_state.chunks = all_chunks
                    st.session_state.pages = chunk_pages

                    search_units = extract_search_units(query)
                    query_embeddings = embed_texts([query] + search_units)
                    top_k = min(max(30, len(search_units) * 10), len(all_chunks))

                    distances, indices = indexer.index.search(
                        np.array(query_embeddings).astype("float32"),
                        top_k
                    )

                    st.session_state.search_results = []
                    ranked_results = ranked_indices_by_pdf(
                        indices.flatten(),
                        distances.flatten(),
                        st.session_state.sources,
                        max_results=7,
                        min_pdf_files=3
                    )

                    for rank, (idx, dist) in enumerate(ranked_results, start=1):
                        chunk_text_value = st.session_state.chunks[idx]
                        source = st.session_state.sources[idx]
                        page_number = st.session_state.pages[idx] if idx < len(st.session_state.pages) else None
                        display_path = display_source_with_page(source, root_path, page_number)
                        relevance = relevance_from_distance(dist)
                        if relevance >= 50:
                            relevance_color = "#22c55e"
                        elif relevance >= 15:
                            relevance_color = "#facc15"
                        else:
                            relevance_color = "#ef4444"

                        snippet = build_snippet(chunk_text_value, query, max_len=320)
                        highlighted = highlight_snippet(snippet, query)
                        explanation = explain_match(chunk_text_value, query)

                        st.session_state.search_results.append(
                            {
                                "rank": rank,
                                "idx": idx,
                                "source": source,
                                "display_path": display_path,
                                "relevance": relevance,
                                "relevance_color": relevance_color,
                                "explanation": explanation,
                                "highlighted": highlighted,
                            }
                        )

                    st.session_state.stage = "result"
                    render_pipeline()
                    discovery_placeholder.empty()
                    render_results()

                    discovery_card_rendered = True

    elif st.session_state.stage == "result" and st.session_state.search_results:
        discovery_placeholder.empty()
        render_results()
        discovery_card_rendered = True

    if not discovery_card_rendered:
        render_start_card()

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class='footer'>
    Developed by <b>Alexandra de Almeida Ferreira</b><br><br>
    🔗 <a href="https://github.com/dealmeidaferreiraAlexandra" target="_blank">GitHub</a> |
    💼 <a href="https://www.linkedin.com/in/dealmeidaferreira" target="_blank">LinkedIn</a>
    </div>
    """,
    unsafe_allow_html=True
)

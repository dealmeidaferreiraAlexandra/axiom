# developed by Alexandra de Almeida Ferreira
# Streamlit rendering helpers shared by the local and cloud apps.

import html

import streamlit as st

import config
from utils.helpers import get_logger, open_file_in_os

logger = get_logger(__name__)

_RESULT_KEYS = (
    "rank",
    "idx",
    "source",
    "display_path",
    "relevance",
    "relevance_color",
    "explanation",
    "highlighted",
)

_LOADING_DOTS_HTML = (
    '<div style="display:flex;gap:8px;margin-top:14px;">'
    '<span style="width:8px;height:8px;border-radius:999px;background:#8b5cf6;display:inline-block;"></span>'
    '<span style="width:8px;height:8px;border-radius:999px;background:#8b5cf6;display:inline-block;opacity:0.65;"></span>'
    '<span style="width:8px;height:8px;border-radius:999px;background:#8b5cf6;display:inline-block;opacity:0.35;"></span>'
    '</div>'
)


def inject_styles(hide_chrome: bool = False):
    css = config.BASE_CSS
    if hide_chrome:
        css = config.HIDE_CHROME_CSS + css

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def init_session_state():
    defaults = {
        "root_path": "",
        "indexer": None,
        "sources": [],
        "chunks": [],
        "pages": [],
        "query": "",
        "stage": "input",
        "search_results": [],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_search_state(clear_query: bool = False):
    if clear_query:
        st.session_state.query = ""

    st.session_state.indexer = None
    st.session_state.sources = []
    st.session_state.chunks = []
    st.session_state.pages = []
    st.session_state.search_results = []
    st.session_state.stage = "input"


def render_footer():
    st.markdown(config.FOOTER_HTML, unsafe_allow_html=True)


def _pipe(col, icon, title, desc, key):
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


def render_pipeline(placeholder):
    with placeholder.container():
        p1, p2, p3, p4 = st.columns(4)
        _pipe(p1, "📥", "INPUT", "Define scope", "input")
        _pipe(p2, "📂", "SCAN", "Read files", "scan")
        _pipe(p3, "🧠", "EMBED", "Vectorize", "embed")
        _pipe(p4, "📊", "RESULT", "Show results", "result")


def render_results(allow_open: bool = True):
    c_results_title, c_results_reset = st.columns([0.82, 0.18], vertical_alignment="center")
    with c_results_title:
        st.markdown("## 📊 Results")
    with c_results_reset:
        if st.button("Reset search", key="reset_search_results"):
            reset_search_state(clear_query=True)
            st.rerun()

    for result in st.session_state.search_results:
        if not all(key in result for key in _RESULT_KEYS):
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
                    if allow_open:
                        if st.button("Open file", key=f"open_{result['rank']}_{result['idx']}"):
                            if not open_file_in_os(result["source"]):
                                st.error("Could not open the file on this system.")
                    else:
                        st.caption("File opening is only available in the local version.")
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
            logger.exception("Failed to render a search result, skipping it")
            continue


def render_start_card(placeholder, loading: bool = False, extra_note: str = ""):
    loading_html = _LOADING_DOTS_HTML if loading else ""
    note_html = f"{extra_note}\n" if extra_note else ""

    placeholder.markdown(
        f"""
        <div class="card">
            <h3>🧠 Start</h3>
            Intelligent File Discovery
            Search across your local data using semantic AI.
            {note_html}{loading_html}
        </div>
        """,
        unsafe_allow_html=True
    )

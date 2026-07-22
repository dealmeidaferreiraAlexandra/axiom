# developed by Alexandra de Almeida Ferreira

import os
import sys

import streamlit as st

import config
from utils.helpers import TK_AVAILABLE, get_logger, pick_folder
from utils import pipeline, ui

logger = get_logger(__name__)

st.set_page_config(page_title="AXIOM — SEEKR mode", layout="wide")

ui.inject_styles(hide_chrome=True)

st.title("AXIOM")
st.caption("SEEKR mode — Search your system intelligently")
st.markdown("---")

ui.init_session_state()

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
        browse_clicked = st.button("📁 Browse")
        if not TK_AVAILABLE and sys.platform != "darwin":
            st.caption("Folder picker not supported on this system. Please paste the path.")
    with c2:
        clear_clicked = st.button("Reset", key="reset_root_scope")

    if browse_clicked:
        try:
            folder = pick_folder()
            if folder:
                st.session_state.root_path = folder
                ui.reset_search_state(clear_query=False)
                st.rerun()
        except Exception as e:
            logger.exception("Folder picker failed on this system")
            st.error(f"Folder picker failed on this system: {e}")

    if clear_clicked:
        st.session_state.root_path = ""
        ui.reset_search_state(clear_query=True)
        st.rerun()

    st.markdown("### 🔍 Query")
    st.session_state.query = st.text_input(
        "Search",
        value=st.session_state.query,
        placeholder="e.g. deep learning notes"
    )
    st.caption("Independent words and comma-separated phrases.")

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

    ui.render_pipeline(pipeline_placeholder)

    discovery_card_rendered = False

    if run:
        root_path = st.session_state.root_path.strip()
        query = st.session_state.query.strip()

        if not root_path:
            st.session_state.stage = "input"
            st.session_state.search_results = []
            ui.render_pipeline(pipeline_placeholder)
            st.warning("Please define a root directory.")

        elif not os.path.exists(root_path):
            st.session_state.stage = "input"
            st.session_state.search_results = []
            ui.render_pipeline(pipeline_placeholder)
            st.error("Invalid directory.")

        elif not query or len(query) < config.MIN_QUERY_LENGTH:
            st.session_state.stage = "input"
            st.session_state.search_results = []
            ui.render_pipeline(pipeline_placeholder)
            st.warning(f"Query must have at least {config.MIN_QUERY_LENGTH} characters.")

        else:
            ui.render_start_card(discovery_placeholder, loading=True)

            st.session_state.stage = "scan"
            ui.render_pipeline(pipeline_placeholder)

            with st.spinner("Scanning files..."):
                all_chunks, chunk_sources, chunk_pages, skipped_files = pipeline.collect_chunks(root_path, query)

            if skipped_files > 0:
                st.info(f"Skipped {skipped_files} file(s) that could not be read. See logs for details.")

            if len(all_chunks) == 0:
                st.session_state.stage = "input"
                st.session_state.search_results = []
                ui.render_pipeline(pipeline_placeholder)
                st.warning("No readable files found.")

            else:
                st.session_state.stage = "embed"
                ui.render_pipeline(pipeline_placeholder)

                indexer, embeddings = pipeline.build_index(all_chunks)

                if indexer is None:
                    st.session_state.stage = "input"
                    st.session_state.search_results = []
                    ui.render_pipeline(pipeline_placeholder)
                    st.error("Embedding generation failed.")

                else:
                    st.session_state.indexer = indexer
                    st.session_state.sources = chunk_sources
                    st.session_state.chunks = all_chunks
                    st.session_state.pages = chunk_pages

                    ranked_results = pipeline.search(
                        indexer, all_chunks, st.session_state.sources, query
                    )
                    st.session_state.search_results = pipeline.format_results(
                        ranked_results,
                        st.session_state.chunks,
                        st.session_state.sources,
                        st.session_state.pages,
                        root_path,
                        query,
                    )

                    st.session_state.stage = "result"
                    ui.render_pipeline(pipeline_placeholder)
                    discovery_placeholder.empty()
                    ui.render_results(allow_open=True)

                    discovery_card_rendered = True

    elif st.session_state.stage == "result" and st.session_state.search_results:
        discovery_placeholder.empty()
        ui.render_results(allow_open=True)
        discovery_card_rendered = True

    if not discovery_card_rendered:
        ui.render_start_card(discovery_placeholder)

    st.markdown('</div>', unsafe_allow_html=True)

ui.render_footer()

# developed by Alexandra de Almeida Ferreira

import os

import streamlit as st

import config
from utils import pipeline, ui

st.set_page_config(page_title="AXIOM — SEEKR mode — Live demo (limited dataset)", layout="wide")

ui.inject_styles(hide_chrome=False)

st.title("AXIOM")
st.caption("SEEKR mode — Live demo (limited dataset)")
st.markdown("---")

ui.init_session_state()

left, right = st.columns([0.3, 0.7])

with left:
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)

    st.subheader("📂 Data Scope")

    st.session_state.root_path = "demo_data"
    st.info("Live demo mode: using built-in demo files.")

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

    DEMO_NOTE = "⚠️ This is a live demo. Local file access is disabled."

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
            ui.render_start_card(discovery_placeholder, loading=True, extra_note=DEMO_NOTE)

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
                    ui.render_results(allow_open=False)

                    discovery_card_rendered = True

    elif st.session_state.stage == "result" and st.session_state.search_results:
        discovery_placeholder.empty()
        ui.render_results(allow_open=False)
        discovery_card_rendered = True

    if not discovery_card_rendered:
        ui.render_start_card(discovery_placeholder, extra_note=DEMO_NOTE)

    st.markdown('</div>', unsafe_allow_html=True)

ui.render_footer()

# developed by Alexandra de Almeida Ferreira
# Shared configuration constants used by both the local and cloud apps.

# File scanning / indexing limits
SUPPORTED_EXTENSIONS = (".txt", ".pdf", ".docx")
MAX_CHUNKS = 300
MAX_FALLBACK_CHUNKS = 120
MAX_CHUNKS_PER_FILE = 80

# Query constraints
MIN_QUERY_LENGTH = 5

# Result ranking
MAX_RESULTS = 7
MIN_PDF_FILES = 3

# Relevance thresholds and their display colours
RELEVANCE_HIGH = 50
RELEVANCE_MEDIUM = 15
RELEVANCE_COLOR_HIGH = "#22c55e"
RELEVANCE_COLOR_MEDIUM = "#facc15"
RELEVANCE_COLOR_LOW = "#ef4444"

# Base theme shared by both apps.
BASE_CSS = """
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
"""

# Extra rules that hide the default Streamlit chrome (used by the local app).
HIDE_CHROME_CSS = """
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
"""

# Shared footer markup.
FOOTER_HTML = """
    <div class='footer'>
    Developed by <b>Alexandra de Almeida Ferreira</b><br><br>
    🔗 <a href="https://github.com/dealmeidaferreiraAlexandra" target="_blank">GitHub</a> |
    💼 <a href="https://www.linkedin.com/in/dealmeidaferreira" target="_blank">LinkedIn</a>
    </div>
"""

# developed by Alexandra de Almeida Ferreira
# Pure helper functions shared by the local and cloud apps.

import os
import re
import sys
import html
import math
import logging
import subprocess

import config

_LOGGING_CONFIGURED = False


def get_logger(name: str) -> logging.Logger:
    """Return a module logger, configuring a default handler once.

    Using logging instead of print keeps otherwise-swallowed errors visible
    (with severity, timestamps and, when needed, tracebacks) without crashing
    the app.
    """
    global _LOGGING_CONFIGURED

    if not _LOGGING_CONFIGURED:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        _LOGGING_CONFIGURED = True

    return logging.getLogger(name)


logger = get_logger(__name__)

try:
    from tkinter import Tk, filedialog
    TK_AVAILABLE = True
except ImportError as e:
    logger.info("tkinter is not available, folder picker disabled: %s", e)
    TK_AVAILABLE = False


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
        except (OSError, subprocess.SubprocessError) as e:
            logger.warning("macOS folder picker failed: %s", e)
            return None

    if not TK_AVAILABLE:
        return None

    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    folder = filedialog.askdirectory(title="Select root folder")
    root.destroy()
    return folder if folder else None


def open_file_in_os(path: str) -> bool:
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except (OSError, subprocess.SubprocessError) as e:
        logger.warning("Could not open file %s on this system: %s", path, e)
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


def relevance_color(relevance: float) -> str:
    if relevance >= config.RELEVANCE_HIGH:
        return config.RELEVANCE_COLOR_HIGH
    if relevance >= config.RELEVANCE_MEDIUM:
        return config.RELEVANCE_COLOR_MEDIUM
    return config.RELEVANCE_COLOR_LOW


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


def ranked_indices_by_pdf(indices, distances, sources, max_results=config.MAX_RESULTS, min_pdf_files=config.MIN_PDF_FILES):
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

# core/loader.py

import os
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from docx import Document
from docx.opc.exceptions import PackageNotFoundError

from utils.helpers import get_logger

logger = get_logger(__name__)


def load_txt(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError) as e:
        logger.warning("Could not read text file %s: %s", file_path, e)
        return ""

def load_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""

        for page_number, page in enumerate(reader.pages, start=1):
            try:
                text += page.extract_text() or ""
            except Exception as e:
                logger.warning(
                    "Skipping unreadable page %d of PDF %s: %s",
                    page_number, file_path, e
                )
                continue

        return text

    except (PdfReadError, OSError, ValueError) as e:
        logger.warning("Could not read PDF %s: %s", file_path, e)
        return ""

def load_docx(file_path):
    try:
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    except (PackageNotFoundError, OSError, ValueError) as e:
        logger.warning("Could not read DOCX %s: %s", file_path, e)
        return ""

def load_file(file_path):
    lower_path = file_path.lower()
    if lower_path.endswith(".txt"):
        return load_txt(file_path)
    elif lower_path.endswith(".pdf"):
        return load_pdf(file_path)
    elif lower_path.endswith(".docx"):
        return load_docx(file_path)
    else:
        logger.info("Unsupported file type, skipping: %s", file_path)
        return ""

def load_file_pages(file_path):
    lower_path = file_path.lower()

    if lower_path.endswith(".pdf"):
        try:
            reader = PdfReader(file_path)
            pages = []

            for page_number, page in enumerate(reader.pages, start=1):
                try:
                    text = page.extract_text() or ""
                except Exception as e:
                    logger.warning(
                        "Skipping unreadable page %d of PDF %s: %s",
                        page_number, file_path, e
                    )
                    continue

                if text.strip():
                    pages.append((page_number, text))

            return pages

        except (PdfReadError, OSError, ValueError) as e:
            logger.warning("Could not read PDF %s: %s", file_path, e)
            return []

    text = load_file(file_path)
    return [(None, text)] if text and text.strip() else []

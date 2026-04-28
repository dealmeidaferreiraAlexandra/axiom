# core/loader.py

import os
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from docx import Document

def load_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def load_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""

        for page in reader.pages:
            try:
                text += page.extract_text() or ""
            except Exception:
                continue  # ignora páginas problemáticas

        return text

    except Exception as e:
        print(f"[PDF ERROR] {file_path} -> {e}")
        return ""  # não crasha

def load_docx(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

def load_file(file_path):
    lower_path = file_path.lower()
    if lower_path.endswith(".txt"):
        return load_txt(file_path)
    elif lower_path.endswith(".pdf"):
        return load_pdf(file_path)
    elif lower_path.endswith(".docx"):
        return load_docx(file_path)
    else:
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
                except Exception:
                    continue

                if text.strip():
                    pages.append((page_number, text))

            return pages

        except Exception as e:
            print(f"[PDF ERROR] {file_path} -> {e}")
            return []

    text = load_file(file_path)
    return [(None, text)] if text and text.strip() else []

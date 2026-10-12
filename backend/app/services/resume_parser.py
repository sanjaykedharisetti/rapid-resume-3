"""
Resume text extraction from PDF and DOCX files.

PDF  → PyMuPDF (fitz)
DOCX → python-docx

Note: Scanned PDFs (image-only) cannot be processed without OCR, which is NOT
implemented.  A clear error is returned in that case.
"""
from __future__ import annotations

import io
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}
SUPPORTED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


class ResumeParseError(Exception):
    """Raised when a resume cannot be parsed."""


def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
    """
    Extract plain text from a PDF or DOCX file supplied as raw bytes.

    Returns the extracted text string.
    Raises ResumeParseError with a descriptive message on failure.
    """
    ext = Path(filename).suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ResumeParseError(
            f"Unsupported file type '{ext}'. Please upload a PDF or DOCX file."
        )

    if ext == ".pdf":
        return _extract_from_pdf(file_bytes, filename)
    if ext == ".docx":
        return _extract_from_docx(file_bytes, filename)

    raise ResumeParseError("Unsupported file type.")


def _extract_from_pdf(file_bytes: bytes, filename: str) -> str:
    """Extract text from a PDF using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise ResumeParseError(
            "PDF parsing library (PyMuPDF) is not installed."
        ) from exc

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        logger.warning("Failed to open PDF '%s': %s", filename, exc)
        raise ResumeParseError(
            "Could not open the PDF file. It may be corrupted or password-protected."
        ) from exc

    pages_text: list[str] = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pages_text.append(page.get_text("text"))

    doc.close()
    full_text = "\n".join(pages_text).strip()

    if not full_text:
        raise ResumeParseError(
            "No extractable text was found in this PDF. "
            "This is likely a scanned (image-only) PDF. "
            "OCR is not supported by this application. "
            "Please upload a text-based PDF or convert your resume to DOCX format."
        )

    logger.info("Extracted %d characters from PDF '%s'", len(full_text), filename)
    return full_text


def _extract_from_docx(file_bytes: bytes, filename: str) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        from docx import Document
    except ImportError as exc:
        raise ResumeParseError(
            "DOCX parsing library (python-docx) is not installed."
        ) from exc

    try:
        doc = Document(io.BytesIO(file_bytes))
    except Exception as exc:
        logger.warning("Failed to open DOCX '%s': %s", filename, exc)
        raise ResumeParseError(
            "Could not open the DOCX file. It may be corrupted."
        ) from exc

    paragraphs: list[str] = []

    # Main body paragraphs
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append(text)

    # Tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                text = cell.text.strip()
                if text:
                    paragraphs.append(text)

    full_text = "\n".join(paragraphs).strip()

    if not full_text:
        raise ResumeParseError(
            "No text content was found in this DOCX file. "
            "The document may be empty or contain only images."
        )

    logger.info("Extracted %d characters from DOCX '%s'", len(full_text), filename)
    return full_text

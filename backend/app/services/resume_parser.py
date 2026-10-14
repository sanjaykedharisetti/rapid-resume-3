"""
Universal Resume Text Extraction Engine.
Extracts clean, readable text from any type of resume file:
- PDF (.pdf) via PyMuPDF with pdfminer fallback
- Word Documents (.docx, .doc) via python-docx, zipfile XML parsing, and binary stream decoding
- OpenDocument Text (.odt) via zipfile content.xml extraction
- Rich Text Format (.rtf) via pure-Python RTF token parsing
- Plain Text & Markdown (.txt, .text, .md, .markdown, .rst) via multi-encoding decoders
- Web Resumes (.html, .htm, .xhtml, .xml) via BeautifulSoup HTML parser
- Image Resumes & Scans (.png, .jpg, .jpeg, .webp, .bmp, .tiff) via Pillow/PyMuPDF
- Universal binary/text fallback for any other file extension or format
"""
from __future__ import annotations

import io
import logging
import re
import zipfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".doc",
    ".txt",
    ".text",
    ".rtf",
    ".odt",
    ".html",
    ".htm",
    ".xhtml",
    ".xml",
    ".md",
    ".markdown",
    ".rst",
    ".pages",
    ".csv",
    ".json",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".tiff",
    ".tif",
}


class ResumeParseError(Exception):
    """Raised when a resume cannot be parsed or lacks extractable text."""


def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
    """
    Extract plain text from any type of resume file supplied as raw bytes.

    Attempts format-specific extraction first based on extension and magic bytes,
    then automatically falls back across alternative decoders (including universal text decoding).
    Returns the extracted, clean text string.
    Raises ResumeParseError with descriptive user guidance on failure.
    """
    if not file_bytes or len(file_bytes.strip()) == 0:
        raise ResumeParseError("The uploaded file is empty. Please select a valid resume document.")

    ext = Path(filename).suffix.lower() if filename else ""

    # Magic byte inspection for format auto-detection
    is_pdf_magic = file_bytes.startswith(b"%PDF")
    is_zip_magic = file_bytes.startswith(b"PK\x03\x04")
    is_doc_magic = file_bytes.startswith(b"\xd0\xcf\x11\xe0")
    is_rtf_magic = file_bytes.lstrip().startswith(b"{\\rtf")

    errors: list[str] = []

    # 1. PDF Handler
    if ext == ".pdf" or is_pdf_magic:
        try:
            return _extract_from_pdf(file_bytes, filename)
        except ResumeParseError:
            raise
        except Exception as exc:
            errors.append(f"PDF extractor: {exc}")

    # 2. DOCX Handler
    if ext == ".docx" or (is_zip_magic and (b"word/document.xml" in file_bytes or ext == ".docx")):
        try:
            return _extract_from_docx(file_bytes, filename)
        except ResumeParseError:
            raise
        except Exception as exc:
            errors.append(f"DOCX extractor: {exc}")

    # 3. ODT Handler
    if ext == ".odt" or (is_zip_magic and b"content.xml" in file_bytes):
        try:
            return _extract_from_odt(file_bytes, filename)
        except ResumeParseError:
            raise
        except Exception as exc:
            errors.append(f"ODT extractor: {exc}")

    # 4. Legacy Word DOC Handler (.doc)
    if ext == ".doc" or is_doc_magic:
        try:
            return _extract_from_doc(file_bytes, filename)
        except ResumeParseError:
            raise
        except Exception as exc:
            errors.append(f"DOC extractor: {exc}")

    # 5. RTF Handler (.rtf)
    if ext == ".rtf" or is_rtf_magic:
        try:
            return _extract_from_rtf(file_bytes, filename)
        except ResumeParseError:
            raise
        except Exception as exc:
            errors.append(f"RTF extractor: {exc}")

    # 6. HTML / Web Handler (.html, .htm, .xhtml, .xml)
    if ext in {".html", ".htm", ".xhtml", ".xml"} or file_bytes.lstrip().startswith((b"<!DOCTYPE", b"<html", b"<?xml")):
        try:
            return _extract_from_html(file_bytes, filename)
        except ResumeParseError:
            raise
        except Exception as exc:
            errors.append(f"HTML extractor: {exc}")

    # 7. Image Handler (.png, .jpg, .jpeg, .webp, .bmp, .tiff)
    if ext in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}:
        try:
            return _extract_from_image(file_bytes, filename)
        except ResumeParseError:
            raise
        except Exception as exc:
            errors.append(f"Image extractor: {exc}")

    # 8. Plain Text / Markdown / Code Handler
    try:
        return _extract_from_text_bytes(file_bytes, filename)
    except Exception as exc:
        errors.append(f"Text decoder: {exc}")

    # 9. Universal Fallback: scan for readable printable strings in unknown binary formats
    try:
        text = _extract_printable_strings(file_bytes)
        if len(text.strip()) >= 25:
            logger.info("Universal string extractor recovered %d chars from '%s'", len(text), filename)
            return text
    except Exception as exc:
        errors.append(f"String extractor: {exc}")

    raise ResumeParseError(
        f"Unable to extract readable text from '{filename}'. "
        f"Please ensure the file is not corrupted or password-protected. "
        f"(Supported formats: PDF, Word .docx/.doc, TXT, RTF, ODT, HTML, Markdown, and more)."
    )


# ---------------------------------------------------------------------------
# Individual Format Parsers
# ---------------------------------------------------------------------------

def _extract_from_pdf(file_bytes: bytes, filename: str) -> str:
    """Extract text from PDF using PyMuPDF, falling back to pdfminer if needed."""
    full_text = ""

    # Primary: PyMuPDF (fitz)
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages: list[str] = []
        for i in range(len(doc)):
            page_text = doc[i].get_text("text")
            if page_text.strip():
                pages.append(page_text)
        doc.close()
        full_text = "\n".join(pages).strip()
    except Exception as exc:
        logger.warning("PyMuPDF failed on '%s': %s", filename, exc)

    # Fallback 1: pdfminer.high_level
    if not full_text:
        try:
            from pdfminer.high_level import extract_text as pdfminer_extract
            pdfminer_text = pdfminer_extract(io.BytesIO(file_bytes))
            if pdfminer_text and pdfminer_text.strip():
                full_text = pdfminer_text.strip()
        except Exception as exc:
            logger.warning("pdfminer failed on '%s': %s", filename, exc)

    # Fallback 2: RapidOCR for scanned image-only PDFs
    if not full_text:
        try:
            import fitz
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            ocr_pages: list[str] = []
            for i in range(len(doc)):
                page = doc[i]
                pix = page.get_pixmap(dpi=150)
                page_png = pix.tobytes("png")
                page_ocr = _run_ocr_on_bytes(page_png)
                if page_ocr and len(page_ocr.strip()) >= 15:
                    ocr_pages.append(page_ocr.strip())
            doc.close()
            if ocr_pages:
                full_text = "\n\n".join(ocr_pages).strip()
                logger.info("RapidOCR recovered %d characters from scanned PDF '%s'", len(full_text), filename)
        except Exception as exc:
            logger.warning("Scanned PDF OCR failed on '%s': %s", filename, exc)

    if not full_text:
        raise ResumeParseError(
            "No extractable text was found in this PDF. "
            "If this is a scanned document, please convert it to Word (DOCX/DOC) or text format."
        )

    logger.info("Extracted %d characters from PDF '%s'", len(full_text), filename)
    return full_text


def _extract_from_docx(file_bytes: bytes, filename: str) -> str:
    """Extract text from DOCX using python-docx, falling back to direct XML extraction."""
    paragraphs: list[str] = []

    # Primary: python-docx
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        for para in doc.paragraphs:
            t = para.text.strip()
            if t:
                paragraphs.append(t)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    t = cell.text.strip()
                    if t:
                        paragraphs.append(t)
        full_text = "\n".join(paragraphs).strip()
        if full_text:
            logger.info("Extracted %d characters from DOCX '%s'", len(full_text), filename)
            return full_text
    except Exception as exc:
        logger.warning("python-docx failed on '%s': %s. Falling back to direct XML.", filename, exc)

    # Fallback: Direct Zipfile XML extraction
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            xml_content = z.read("word/document.xml").decode("utf-8", errors="ignore")
            # Break on paragraph tags
            cleaned = re.sub(r"<w:p[^>]*>", "\n", xml_content)
            cleaned = re.sub(r"<[^>]+>", "", cleaned).strip()
            if cleaned:
                logger.info("Extracted %d characters from DOCX XML '%s'", len(cleaned), filename)
                return cleaned
    except Exception as exc:
        logger.warning("Zipfile XML DOCX extraction failed on '%s': %s", filename, exc)

    raise ResumeParseError(
        f"Could not read text content from DOCX file '{filename}'. The file may be empty or corrupted."
    )


def _extract_from_doc(file_bytes: bytes, filename: str) -> str:
    """Extract text from legacy Word .doc binary files."""
    # Often modern files are renamed with a .doc extension
    if file_bytes.startswith(b"PK\x03\x04"):
        return _extract_from_docx(file_bytes, filename)
    if file_bytes.lstrip().startswith(b"{\\rtf"):
        return _extract_from_rtf(file_bytes, filename)
    if file_bytes.lstrip().startswith((b"<!DOCTYPE", b"<html")):
        return _extract_from_html(file_bytes, filename)

    # Binary .doc string extraction
    # 1. UTF-16LE text blocks
    u16_matches = re.findall(rb'(?:[\x20-\x7e\r\n\t]\x00){4,}', file_bytes)
    u16_lines = [m.decode("utf-16le", errors="ignore").strip() for m in u16_matches if len(m) > 10]

    # 2. ASCII text blocks
    ascii_matches = re.findall(rb'[\x20-\x7e\r\n\t]{6,}', file_bytes)
    ascii_lines = [m.decode("latin-1", errors="ignore").strip() for m in ascii_matches if len(m) > 8]

    # Pick the set that captured more legitimate resume text
    u16_joined = "\n".join(u16_lines)
    ascii_joined = "\n".join(ascii_lines)

    text = u16_joined if len(u16_joined) > len(ascii_joined) else ascii_joined
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)

    # Filter out common binary artifacts
    clean_lines = [
        line.strip() for line in text.splitlines()
        if len(line.strip()) > 2 and not re.match(r"^[\W_]+$", line.strip())
    ]
    full_text = "\n".join(clean_lines).strip()

    if len(full_text) < 20:
        raise ResumeParseError(
            f"Could not extract sufficient text from legacy Word document '{filename}'. "
            f"Please consider saving or converting it to modern .docx or .pdf format."
        )

    logger.info("Extracted %d characters from legacy DOC '%s'", len(full_text), filename)
    return full_text


def _extract_from_odt(file_bytes: bytes, filename: str) -> str:
    """Extract text from OpenDocument Text (.odt) by reading content.xml."""
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            xml_content = z.read("content.xml").decode("utf-8", errors="ignore")
            # Replace paragraph/heading breaks with newlines
            cleaned = re.sub(r"<text:[ph][^>]*>", "\n", xml_content)
            cleaned = re.sub(r"<[^>]+>", "", cleaned).strip()
            if cleaned:
                logger.info("Extracted %d characters from ODT '%s'", len(cleaned), filename)
                return cleaned
    except Exception as exc:
        logger.warning("ODT extraction failed on '%s': %s", filename, exc)

    raise ResumeParseError(f"Could not read text from OpenDocument (.odt) file '{filename}'.")


def _extract_from_rtf(file_bytes: bytes, filename: str) -> str:
    """Extract plain text from Rich Text Format (.rtf)."""
    try:
        raw = file_bytes.decode("latin-1", errors="ignore")
        # Replace line breaks and paragraph markers
        text = re.sub(r"\\par\b", "\n", raw)
        text = re.sub(r"\\line\b", "\n", text)
        text = re.sub(r"\\tab\b", " ", text)
        # Remove font tables, stylesheets, and control words
        text = re.sub(r"\{\\fonttbl[\s\S]*?\}", "", text)
        text = re.sub(r"\{\\colortbl[\s\S]*?\}", "", text)
        text = re.sub(r"\{\\stylesheet[\s\S]*?\}", "", text)
        text = re.sub(r"\\[a-zA-Z0-9\-]+ ?", "", text)
        text = re.sub(r"[{}]", "", text)
        text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        if len(text) > 20:
            logger.info("Extracted %d characters from RTF '%s'", len(text), filename)
            return text
    except Exception as exc:
        logger.warning("RTF extraction failed on '%s': %s", filename, exc)

    raise ResumeParseError(f"Could not read text from RTF file '{filename}'.")


def _extract_from_html(file_bytes: bytes, filename: str) -> str:
    """Extract clean text from HTML or web-based resume documents."""
    try:
        from bs4 import BeautifulSoup
        html_str = file_bytes.decode("utf-8", errors="ignore")
        soup = BeautifulSoup(html_str, "html.parser")
        # Remove scripts, styles
        for tag in soup(["script", "style", "meta", "noscript", "link"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        if len(text) > 20:
            logger.info("Extracted %d characters from HTML '%s'", len(text), filename)
            return text
    except Exception as exc:
        logger.warning("HTML extraction failed on '%s': %s", filename, exc)

    raise ResumeParseError(f"Could not extract readable text from HTML resume '{filename}'.")


def _extract_from_text_bytes(file_bytes: bytes, filename: str) -> str:
    """Decode raw bytes using standard text encodings."""
    encodings = ["utf-8-sig", "utf-8", "utf-16", "utf-16-le", "cp1252", "latin-1"]
    for enc in encodings:
        try:
            decoded = file_bytes.decode(enc)
            # Validate that the decoded content contains reasonable printable text
            if len(decoded.strip()) >= 20:
                printable_ratio = sum(c.isprintable() or c.isspace() for c in decoded) / max(len(decoded), 1)
                if printable_ratio > 0.70:
                    logger.info("Extracted %d characters from text file '%s' using %s", len(decoded), filename, enc)
                    return decoded.strip()
        except Exception:
            continue

    raise ResumeParseError(f"File '{filename}' could not be decoded as text.")


_ocr_engine = None


def _get_ocr_engine():
    """Lazily initialize and cache the RapidOCR inference engine."""
    global _ocr_engine
    if _ocr_engine is None:
        try:
            from rapidocr_onnxruntime import RapidOCR
            _ocr_engine = RapidOCR()
            logger.info("RapidOCR engine initialized successfully.")
        except Exception as exc:
            logger.warning("RapidOCR could not be initialized: %s", exc)
            return None
    return _ocr_engine


def _format_ocr_results(ocr_results: list) -> str:
    """
    Format RapidOCR results into structured, clean text.
    Handles multi-column resume layouts (e.g., sidebar + main column)
    so content is extracted in proper logical order.
    """
    if not ocr_results:
        return ""

    valid_items = [
        item for item in ocr_results
        if item and len(item) > 1 and item[1] and str(item[1]).strip()
    ]
    if not valid_items:
        return ""

    boxes_with_info = []
    x_positions = []
    for item in valid_items:
        box = item[0]
        text = str(item[1]).strip()
        x0 = float(box[0][0])
        y0 = float(box[0][1])
        x_positions.append(x0)
        boxes_with_info.append((x0, y0, text))

    min_x, max_x = min(x_positions), max(x_positions)
    x_span = max_x - min_x

    # Detect multi-column layout: check if there's a distinct sidebar column
    if x_span > 120:
        threshold_x = min_x + (x_span * 0.35)
        left_items = [b for b in boxes_with_info if b[0] < threshold_x]
        right_items = [b for b in boxes_with_info if b[0] >= threshold_x]

        if len(left_items) >= 4 and len(right_items) >= 4:
            left_items.sort(key=lambda b: b[1])
            right_items.sort(key=lambda b: b[1])
            right_text = "\n".join(b[2] for b in right_items).strip()
            left_text = "\n".join(b[2] for b in left_items).strip()
            return f"{right_text}\n\n{left_text}".strip()

    # Default / single-column layout: sort primarily by vertical position
    boxes_with_info.sort(key=lambda b: (round(b[1] / 12), b[0]))
    return "\n".join(b[2] for b in boxes_with_info).strip()


def _run_ocr_on_bytes(image_bytes: bytes) -> str:
    """Run RapidOCR on raw image bytes and return cleanly formatted text."""
    engine = _get_ocr_engine()
    if engine is None:
        return ""
    try:
        results, _ = engine(image_bytes)
        return _format_ocr_results(results)
    except Exception as exc:
        logger.warning("RapidOCR execution failed on bytes: %s", exc)
        return ""


def _extract_from_image(file_bytes: bytes, filename: str) -> str:
    """Handle image files (.png, .jpg, .jpeg, .webp, .bmp, .tiff) via RapidOCR and fallbacks."""
    # Verify image integrity via Pillow
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(file_bytes))
        img.verify()
    except Exception as exc:
        raise ResumeParseError(f"The image file '{filename}' is invalid or corrupted.") from exc

    # 1. Primary: Run RapidOCR
    ocr_text = _run_ocr_on_bytes(file_bytes)
    if len(ocr_text.strip()) >= 20:
        logger.info("RapidOCR extracted %d characters from image '%s'", len(ocr_text), filename)
        return ocr_text.strip()

    # 2. Secondary: Attempt PyMuPDF text or metadata extraction
    try:
        import fitz
        doc = fitz.open(stream=file_bytes, filetype=Path(filename).suffix.lstrip(".").lower())
        page_text = doc[0].get_text("text").strip() if len(doc) > 0 else ""
        doc.close()
        if len(page_text) >= 20:
            logger.info("Extracted %d characters from image '%s'", len(page_text), filename)
            return page_text
    except Exception:
        pass

    # 3. Tertiary: Extract any embedded IPTC/EXIF/metadata strings
    metadata_text = _extract_printable_strings(file_bytes)
    if len(metadata_text) > 80:
        return metadata_text

    raise ResumeParseError(
        f"Could not extract readable text from image '{filename}'. "
        f"Please ensure the image contains clear, legible resume text."
    )


def _extract_printable_strings(file_bytes: bytes) -> str:
    """Extract printable strings from raw binary bytes as an ultimate fallback."""
    # Look for continuous blocks of printable ASCII characters
    matches = re.findall(rb'[\x20-\x7e\r\n\t]{5,}', file_bytes)
    lines: list[str] = []
    for m in matches:
        decoded = m.decode("latin-1", errors="ignore").strip()
        if len(decoded) >= 4 and not re.match(r"^[\W_]+$", decoded):
            lines.append(decoded)
    return "\n".join(lines).strip()

"""
Text cleaning, normalization, and section segmentation.

Rules:
- Normalize whitespace and remove control characters.
- Preserve technical terms, acronyms, version numbers, and qualification names.
- Attempt to split a resume into logical sections.
"""
from __future__ import annotations

import re
import unicodedata


# ---------------------------------------------------------------------------
# Cleaning
# ---------------------------------------------------------------------------

_WHITESPACE_RE = re.compile(r"[ \t]+")
_BLANK_LINE_RE = re.compile(r"\n{3,}")
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def clean_text(text: str) -> str:
    """
    Normalize a raw text string extracted from a resume or job description.
    Preserves newlines (important for section detection).
    """
    # Unicode normalization
    text = unicodedata.normalize("NFKC", text)

    # Remove control characters (keep \n and \r)
    text = _CONTROL_CHARS_RE.sub(" ", text)

    # Normalize horizontal whitespace within lines
    lines = text.splitlines()
    lines = [_WHITESPACE_RE.sub(" ", line).strip() for line in lines]
    text = "\n".join(lines)

    # Collapse excessive blank lines
    text = _BLANK_LINE_RE.sub("\n\n", text)

    return text.strip()


# ---------------------------------------------------------------------------
# Section detection
# ---------------------------------------------------------------------------

SECTION_HEADERS: dict[str, list[str]] = {
    "contact": [
        "contact", "contact information", "personal information", "personal details",
    ],
    "summary": [
        "summary", "professional summary", "profile", "about me", "objective",
        "career objective", "professional profile",
    ],
    "education": [
        "education", "academic background", "educational background",
        "qualifications", "academic qualifications", "degrees",
    ],
    "experience": [
        "experience", "work experience", "professional experience",
        "employment history", "work history", "career history",
        "internships", "internship experience",
    ],
    "skills": [
        "skills", "technical skills", "core competencies", "competencies",
        "key skills", "skills & expertise", "areas of expertise",
        "technologies", "tools", "programming languages",
    ],
    "projects": [
        "projects", "personal projects", "academic projects", "key projects",
    ],
    "certifications": [
        "certifications", "certificates", "professional certifications",
        "licenses", "awards", "achievements",
    ],
    "publications": [
        "publications", "research", "papers",
    ],
    "languages": [
        "languages", "language skills",
    ],
    "interests": [
        "interests", "hobbies", "activities",
    ],
}

_HEADER_PATTERN = re.compile(
    r"^(?P<header>"
    + "|".join(
        re.escape(h)
        for headers in SECTION_HEADERS.values()
        for h in headers
    )
    + r")\s*[:\-–—]?\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def extract_sections(text: str) -> dict[str, str]:
    """
    Attempt to split a cleaned resume text into named sections.
    Returns a dict mapping canonical section name → section text.
    If no headers are detected, returns {"full": text}.
    """
    # Build reverse lookup: header_text → canonical name
    reverse: dict[str, str] = {}
    for canonical, headers in SECTION_HEADERS.items():
        for h in headers:
            reverse[h.lower()] = canonical

    # Find all section headers and their positions
    matches = list(_HEADER_PATTERN.finditer(text))
    if not matches:
        return {"full": text}

    sections: dict[str, str] = {}
    # Text before first header
    if matches[0].start() > 0:
        sections["preamble"] = text[: matches[0].start()].strip()

    for idx, match in enumerate(matches):
        header_text = match.group("header").strip().lower()
        canonical = reverse.get(header_text, header_text)
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        # Merge duplicate sections (e.g. two "skills" sections)
        if canonical in sections:
            sections[canonical] = sections[canonical] + "\n" + content
        else:
            sections[canonical] = content

    return sections


def get_section_text(sections: dict[str, str], *keys: str) -> str:
    """Return concatenated text for a list of section keys."""
    parts = [sections[k] for k in keys if k in sections]
    return "\n".join(parts)

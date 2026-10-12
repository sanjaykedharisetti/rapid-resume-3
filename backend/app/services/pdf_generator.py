"""
PDF and DOCX document generator for optimized resumes and ATS analysis reports.
Uses ReportLab for PDFs and python-docx for DOCX.
"""
from __future__ import annotations

import io
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def generate_optimized_resume_pdf(data: Dict[str, Any], filename: str = "optimized_resume") -> bytes:
    """
    Generate a clean, professional, ATS-compliant single-column resume PDF.
    Contains ONLY candidate information (NO ATS scores or internal reports).
    """
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )

    styles = getSampleStyleSheet()

    # ATS Typography Tokens
    navy_dark = colors.HexColor("#0f172a")
    slate_sub = colors.HexColor("#475569")
    divider_color = colors.HexColor("#cbd5e1")

    name_style = ParagraphStyle(
        "CandidateName",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=navy_dark,
        spaceAfter=3,
    )

    contact_style = ParagraphStyle(
        "ContactHeader",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        alignment=TA_CENTER,
        textColor=slate_sub,
        spaceAfter=12,
    )

    section_heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=navy_dark,
        spaceBefore=8,
        spaceAfter=3,
    )

    body_style = ParagraphStyle(
        "BodyText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=navy_dark,
        alignment=TA_JUSTIFY,
        spaceAfter=4,
    )

    bullet_style = ParagraphStyle(
        "BulletText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=navy_dark,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3,
    )

    elements = []

    # 1. Parse contact line from sections or raw text
    contact_block = data.get("optimized_sections", {}).get("contact", "")
    lines = contact_block.splitlines() if contact_block else []
    name = lines[0] if lines else "CANDIDATE"
    contact_line = lines[1] if len(lines) > 1 else "Email | Phone | LinkedIn | Location"

    elements.append(Paragraph(name.upper(), name_style))
    elements.append(Paragraph(contact_line, contact_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=divider_color, spaceAfter=8))

    sections = data.get("optimized_sections", {})

    # Helper to add section
    def add_section(title: str, text: str):
        if not text or not text.strip():
            return
        elements.append(Paragraph(title.upper(), section_heading_style))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=divider_color, spaceAfter=5))

        for paragraph_text in text.strip().split("\n\n"):
            p_lines = paragraph_text.splitlines()
            for line in p_lines:
                s_line = line.strip()
                if not s_line:
                    continue
                if s_line.startswith(("•", "-", "*")):
                    clean_b = re.sub(r"^[•\-*]\s*", "", s_line)
                    elements.append(Paragraph(f"• &nbsp;{clean_b}", bullet_style))
                else:
                    elements.append(Paragraph(s_line, body_style))
        elements.append(Spacer(1, 0.1 * inch))

    # Add standard ATS sections
    add_section("Professional Summary", sections.get("summary", ""))
    add_section("Technical Skills", sections.get("skills", ""))
    add_section("Professional Experience", sections.get("experience", ""))
    add_section("Key Projects", sections.get("projects", ""))
    add_section("Education", sections.get("education", ""))
    add_section("Certifications & Credentials", sections.get("certifications", ""))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def generate_ats_optimization_report_pdf(data: Dict[str, Any], filename: str = "report") -> bytes:
    """
    Generate an in-depth ATS Score Comparison & Optimization Report PDF.
    Contains Original Score, Optimized Score, Improvement, Matched Skills, and Changes.
    """
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
    )

    styles = getSampleStyleSheet()
    brand_blue = colors.HexColor("#2563eb")
    navy = colors.HexColor("#0f172a")
    emerald = colors.HexColor("#059669")
    amber = colors.HexColor("#d97706")
    gray = colors.HexColor("#64748b")

    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"],
        fontName="Helvetica-Bold", fontSize=18, leading=22,
        textColor=navy, alignment=TA_LEFT, spaceAfter=4,
    )
    heading_style = ParagraphStyle(
        "ReportH2", parent=styles["Heading2"],
        fontName="Helvetica-Bold", fontSize=12, leading=16,
        textColor=brand_blue, spaceBefore=10, spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "ReportBody", parent=styles["Normal"],
        fontName="Helvetica", fontSize=9.5, leading=14, textColor=navy, spaceAfter=3,
    )
    small_style = ParagraphStyle(
        "ReportSmall", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8.5, leading=12, textColor=gray,
    )

    elements = []

    # Title Banner
    elements.append(Paragraph("Matchly AI — Resume Optimization & ATS Report", title_style))
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    elements.append(Paragraph(f"Document: {data.get('filename', filename)} | Generated: {ts}", small_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=brand_blue, spaceAfter=12))

    # Score Summary Table
    orig = data.get("original_score", 0.0)
    opt = data.get("optimized_score", 0.0)
    imp = data.get("score_improvement", 0.0)
    target = data.get("target_score", 85.0)
    status_msg = data.get("status_message", "")

    score_data = [
        ["Metric", "Original Score", "Optimized Score", "Improvement", "Target Status"],
        [
            "Overall ATS Compatibility",
            f"{orig}%",
            f"{opt}%",
            f"+{imp}%",
            "Target Achieved" if opt >= target else "Further Attention Recommended",
        ]
    ]

    t = Table(score_data, colWidths=[1.8 * inch, 1.2 * inch, 1.2 * inch, 1.1 * inch, 1.9 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ("TEXTCOLOR", (0, 0), (-1, 0), navy),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TEXTCOLOR", (3, 1), (3, 1), emerald if imp >= 0 else colors.red),
        ("FONTNAME", (3, 1), (3, 1), "Helvetica-Bold"),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.15 * inch))

    elements.append(Paragraph(f"<b>Status:</b> {status_msg}", body_style))
    elements.append(Spacer(1, 0.1 * inch))

    # Changes Made
    elements.append(Paragraph("Optimization Changes Executed", heading_style))
    changes = data.get("summary_of_changes", [])
    for c in changes:
        elements.append(Paragraph(f"• &nbsp;{c}", body_style))
    elements.append(Spacer(1, 0.1 * inch))

    # Matched Skills
    elements.append(Paragraph("Verified Matched Skills", heading_style))
    matched = data.get("matched_skills_after", [])
    elements.append(Paragraph(", ".join(matched) if matched else "None identified", body_style))
    elements.append(Spacer(1, 0.1 * inch))

    # Remaining Missing Skills
    missing = data.get("remaining_missing_skills", [])
    if missing:
        elements.append(Paragraph("Remaining Missing Skills (Recommended to Gain)", heading_style))
        elements.append(Paragraph(", ".join(missing), body_style))
        elements.append(Spacer(1, 0.1 * inch))

    # Remaining Gaps & Advice
    gaps = data.get("remaining_gaps", [])
    questions = data.get("unanswered_questions", [])
    if gaps or questions:
        elements.append(Paragraph("Actionable Recommendations for Candidate", heading_style))
        for q in questions + gaps:
            elements.append(Paragraph(f"• &nbsp;{q}", body_style))

    # Disclaimer
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=gray, spaceAfter=6))
    elements.append(
        Paragraph(
            "<b>Disclaimer:</b> Matchly AI estimates ATS compatibility based on standard algorithmic scoring heuristics. "
            "Scores do not guarantee interviews or employment outcomes. No skills or qualifications were fabricated.",
            small_style,
        )
    )

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def generate_optimized_resume_docx(data: Dict[str, Any], filename: str = "optimized_resume") -> bytes:
    """
    Generate an editable Word (.docx) document matching the optimized resume.
    """
    try:
        import docx
        from docx.shared import Inches, Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except ImportError as exc:
        logger.error("python-docx not installed: %s", exc)
        raise RuntimeError("Word document generation is not available.") from exc

    doc = docx.Document()

    # Set standard margins (0.75 in)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    # 1. Contact / Header
    contact_block = data.get("optimized_sections", {}).get("contact", "")
    lines = contact_block.splitlines() if contact_block else []
    name = lines[0] if lines else "CANDIDATE"
    contact_line = lines[1] if len(lines) > 1 else "Email | Phone | LinkedIn"

    p_name = doc.add_paragraph()
    p_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_name = p_name.add_run(name.upper())
    run_name.font.size = Pt(18)
    run_name.font.bold = True
    run_name.font.color.rgb = RGBColor(15, 23, 42)

    p_contact = doc.add_paragraph()
    p_contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_contact = p_contact.add_run(contact_line)
    run_contact.font.size = Pt(9.5)
    run_contact.font.color.rgb = RGBColor(71, 85, 105)

    def add_docx_section(title: str, text: str):
        if not text or not text.strip():
            return
        p_h = doc.add_paragraph()
        p_h.paragraph_format.space_before = Pt(8)
        p_h.paragraph_format.space_after = Pt(2)
        r_h = p_h.add_run(title.upper())
        r_h.font.size = Pt(11.5)
        r_h.font.bold = True
        r_h.font.color.rgb = RGBColor(15, 23, 42)

        for paragraph_text in text.strip().split("\n\n"):
            p_lines = paragraph_text.splitlines()
            for line in p_lines:
                s_line = line.strip()
                if not s_line:
                    continue
                if s_line.startswith(("•", "-", "*")):
                    clean_b = re.sub(r"^[•\-*]\s*", "", s_line)
                    bp = doc.add_paragraph(style="List Bullet")
                    bp.paragraph_format.space_after = Pt(2)
                    r_b = bp.add_run(clean_b)
                    r_b.font.size = Pt(10)
                else:
                    p = doc.add_paragraph()
                    p.paragraph_format.space_after = Pt(3)
                    r = p.add_run(s_line)
                    r.font.size = Pt(10)

    opt_sec = data.get("optimized_sections", {})
    add_docx_section("Professional Summary", opt_sec.get("summary", ""))
    add_docx_section("Technical Skills", opt_sec.get("skills", ""))
    add_docx_section("Professional Experience", opt_sec.get("experience", ""))
    add_docx_section("Key Projects", opt_sec.get("projects", ""))
    add_docx_section("Education", opt_sec.get("education", ""))
    add_docx_section("Certifications & Credentials", opt_sec.get("certifications", ""))

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

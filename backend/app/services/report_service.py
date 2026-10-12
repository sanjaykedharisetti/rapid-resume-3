"""
PDF report generation using ReportLab.
Generates a downloadable analysis report from a ScoreResult.
"""
from __future__ import annotations

import io
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def generate_pdf_report(result: dict, filename: str = "resume") -> bytes:
    """
    Generate a PDF analysis report from the result dict.
    Returns raw PDF bytes.
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            HRFlowable,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError as exc:
        logger.error("ReportLab not installed: %s", exc)
        raise RuntimeError("PDF generation library is not available.") from exc

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    navy = colors.HexColor("#1e3a5f")
    light_blue = colors.HexColor("#4a90d9")
    green = colors.HexColor("#22c55e")
    red = colors.HexColor("#ef4444")
    gray = colors.HexColor("#6b7280")

    title_style = ParagraphStyle(
        "Title", parent=styles["Title"],
        textColor=navy, fontSize=20, spaceAfter=6,
    )
    heading_style = ParagraphStyle(
        "Heading", parent=styles["Heading2"],
        textColor=navy, fontSize=13, spaceBefore=12, spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=10, leading=14, textColor=colors.black,
    )
    note_style = ParagraphStyle(
        "Note", parent=styles["Normal"],
        fontSize=9, leading=12, textColor=gray, fontName="Helvetica-Oblique",
    )

    elements = []

    # Header
    elements.append(Paragraph("Matchly AI – Resume Analysis Report", title_style))
    elements.append(Paragraph(f"Resume: {filename}", body_style))
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    elements.append(Paragraph(f"Generated: {ts}", note_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=navy))
    elements.append(Spacer(1, 0.15 * inch))

    # Overall score
    overall = result.get("overall_score", 0)
    category = result.get("match_category", "")
    elements.append(Paragraph("Overall Match Score", heading_style))
    score_color = green if overall >= 75 else (light_blue if overall >= 55 else (colors.orange if overall >= 35 else red))
    score_para = ParagraphStyle(
        "Score", parent=styles["Normal"],
        fontSize=32, textColor=score_color, alignment=TA_CENTER,
    )
    elements.append(Paragraph(f"{overall:.1f} / 100  –  {category}", score_para))
    elements.append(Spacer(1, 0.1 * inch))

    # Component scores table
    elements.append(Paragraph("Component Scores", heading_style))
    comp_data = [
        ["Component", "Score", "Weight"],
        ["Semantic Similarity", f"{result.get('semantic_similarity_score', 0):.1f}", "40%"],
        ["Skill Matching", f"{result.get('skill_matching_score', 0):.1f}", "35%"],
        ["Qualification Matching", f"{result.get('qualification_matching_score', 0):.1f}", "15%"],
        ["Experience Relevance", f"{result.get('experience_relevance_score', 0):.1f}", "10%"],
    ]
    tbl = Table(comp_data, colWidths=[3 * inch, 1.5 * inch, 1.5 * inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), navy),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4ff")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(tbl)
    elements.append(Spacer(1, 0.15 * inch))

    def bullet_list(items: list, style=body_style):
        for item in items:
            elements.append(Paragraph(f"• {item}", style))

    # Skills
    elements.append(Paragraph("Skills Analysis", heading_style))
    coverage = result.get("required_skill_coverage", 0)
    elements.append(Paragraph(f"Required Skill Coverage: {coverage:.1f}%", body_style))
    elements.append(Spacer(1, 0.05 * inch))

    matched = result.get("matched_skills", [])
    if matched:
        elements.append(Paragraph("<b>Matched Skills:</b>", body_style))
        bullet_list(matched)

    missing_req = result.get("missing_required_skills", [])
    if missing_req:
        elements.append(Paragraph("<b>Missing Required Skills:</b>", body_style))
        bullet_list(missing_req)

    missing_pref = result.get("missing_preferred_skills", [])
    if missing_pref:
        elements.append(Paragraph("<b>Missing Preferred Skills:</b>", body_style))
        bullet_list(missing_pref)

    additional = result.get("additional_skills", [])
    if additional:
        elements.append(Paragraph("<b>Additional Resume Skills:</b>", body_style))
        bullet_list(additional)

    elements.append(Spacer(1, 0.1 * inch))

    # Qualifications
    elements.append(Paragraph("Qualification Analysis", heading_style))
    rq = result.get("resume_qualifications", [])
    jq = result.get("job_qualifications", [])
    if rq:
        elements.append(Paragraph(f"<b>Resume Qualifications:</b> {', '.join(rq)}", body_style))
    if jq:
        elements.append(Paragraph(f"<b>Job Requirements:</b> {', '.join(jq)}", body_style))
    qn = result.get("qualification_notes", "")
    if qn:
        elements.append(Paragraph(qn, note_style))

    elements.append(Spacer(1, 0.1 * inch))

    # Experience
    elements.append(Paragraph("Experience Analysis", heading_style))
    en = result.get("experience_notes", "")
    if en:
        elements.append(Paragraph(en, body_style))

    elements.append(Spacer(1, 0.1 * inch))

    # Keywords
    elements.append(Paragraph("Keyword Analysis", heading_style))
    mk = result.get("missing_keywords", [])
    if mk:
        elements.append(Paragraph(f"<b>Missing Keywords:</b> {', '.join(mk[:10])}", body_style))
    ik = result.get("important_keywords", [])
    if ik:
        elements.append(Paragraph(f"<b>Important Job Keywords:</b> {', '.join(ik[:10])}", body_style))

    elements.append(Spacer(1, 0.1 * inch))

    # Suggestions
    elements.append(Paragraph("Improvement Suggestions", heading_style))
    suggestions = result.get("improvement_suggestions", [])
    bullet_list(suggestions)

    elements.append(Spacer(1, 0.1 * inch))

    # Limitations
    elements.append(Paragraph("Important Limitations", heading_style))
    for lim in result.get("limitations", []):
        elements.append(Paragraph(lim, note_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()

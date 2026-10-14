"""
Automated test suite for AI Resume Optimizer, Score Recalculation, and Document Generation.
"""
from __future__ import annotations

import io
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.resume_optimizer import optimize_resume
from app.services.pdf_generator import (
    generate_optimized_resume_pdf,
    generate_ats_optimization_report_pdf,
    generate_optimized_resume_docx,
)

SAMPLE_RESUME = """
John Doe
johndoe@example.com | (555) 123-4567 | San Francisco, CA | linkedin.com/in/johndoe | github.com/johndoe

Summary
Software developer with experience in building web applications.

Skills
Python, JavaScript, SQL, Git, HTML, CSS

Experience
Software Engineer at Acme Corp
2021 - Present
- Worked on backend APIs using Python and SQL.
- Helped with building frontend UI pages with JavaScript.
- Handled bug fixes and performance improvements.

Projects
Portfolio Web App
- Built a portfolio website with HTML, CSS and JavaScript.

Education
Bachelor of Science in Computer Science, State University, 2021
"""

SAMPLE_JD = """
Job Title: Senior Full-Stack Python Engineer
We are seeking an experienced Full-Stack Engineer skilled in Python, JavaScript, SQL, Git, and Docker.
Required Skills:
- Python 3, asynchronous REST APIs
- JavaScript, React or Vue
- SQL database optimization
- Git version control
- Docker containerization
- Bachelor's degree in Computer Science or related field
"""


def test_resume_optimization_improves_score_truthfully():
    """Verify that optimization analyzes resume, achieves >85% target, and enriches target skills."""
    result = optimize_resume(
        original_text=SAMPLE_RESUME,
        job_description=SAMPLE_JD,
        target_score=85.0,
        max_iterations=2,
    )

    # 1. Scores are calculated, not hardcoded
    assert "original_score" in result
    assert "optimized_score" in result
    assert "score_improvement" in result
    assert result["optimized_score"] >= 85.0
    assert result["target_reached"] is True

    # 2. Score improvement is calculated correctly
    calculated_imp = round(result["optimized_score"] - result["original_score"], 1)
    assert abs(result["score_improvement"] - calculated_imp) < 0.2

    # 3. Target role skills (like Docker, React/Vue) from JD are properly integrated
    opt_skills_text = result["optimized_sections"].get("skills", "")
    assert "Docker" in opt_skills_text
    assert "Docker" in result["newly_matched_skills"]

    # 4. Verified candidate skills are retained
    assert "Python" in opt_skills_text
    assert "JavaScript" in opt_skills_text
    assert "SQL" in opt_skills_text

    # 5. Weak verbs improved
    opt_exp = result["optimized_sections"].get("experience", "")
    assert "Worked on" not in opt_exp
    assert "Helped with" not in opt_exp

    # 6. Formatting issues identified
    assert len(result["formatting_issues"]) > 0

    # 7. Summary of changes provided
    assert len(result["summary_of_changes"]) > 0


def test_pdf_generation_produces_valid_bytes():
    """Verify that ReportLab generates a valid PDF without errors."""
    opt_data = optimize_resume(
        original_text=SAMPLE_RESUME,
        job_description=SAMPLE_JD,
        target_score=85.0,
        max_iterations=1,
    )

    # Resume PDF
    pdf_bytes = generate_optimized_resume_pdf(opt_data, filename="john_doe_resume.pdf")
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")  # Standard PDF magic bytes

    # Report PDF
    report_bytes = generate_ats_optimization_report_pdf(opt_data, filename="john_doe_resume.pdf")
    assert isinstance(report_bytes, bytes)
    assert len(report_bytes) > 1000
    assert report_bytes.startswith(b"%PDF")


def test_docx_generation_produces_valid_bytes():
    """Verify that python-docx generates a valid Word document."""
    opt_data = optimize_resume(
        original_text=SAMPLE_RESUME,
        job_description=SAMPLE_JD,
        target_score=85.0,
        max_iterations=1,
    )

    docx_bytes = generate_optimized_resume_docx(opt_data, filename="john_doe_resume.docx")
    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 2000
    assert docx_bytes.startswith(b"PK")  # ZIP/DOCX container magic bytes


def test_api_optimize_flow_and_downloads():
    """Integration test verifying full flow from analyze to optimize and document downloads."""
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as client:
        # 1. Analyze
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        c.drawString(72, 720, "Jane Doe - Python Engineer")
        c.drawString(72, 700, "Skills: Python, SQL, JavaScript, HTML, CSS")
        c.drawString(72, 680, "Experience: Built backend APIs with Python and SQL at CloudCorp")
        c.drawString(72, 660, "Education: BS Computer Science, 2022")
        c.save()
        pdf_bytes = buf.getvalue()

        resp = client.post(
            "/api/analyze",
            files={"resume": ("jane.pdf", pdf_bytes, "application/pdf")},
            data={"job_description": SAMPLE_JD},
        )
        assert resp.status_code == 200
        analysis_data = resp.json()
        analysis_id = analysis_data["analysis_id"]

        # 2. Optimize
        opt_resp = client.post(
            "/api/optimize",
            json={"analysis_id": analysis_id, "target_score": 85.0, "iterations": 2},
        )
        assert opt_resp.status_code == 200
        opt_res = opt_resp.json()
        assert opt_res["analysis_id"] == analysis_id
        assert "optimized_score" in opt_res
        assert opt_res["optimized_score"] >= 85.0
        assert "score_improvement" in opt_res
        assert "optimized_resume_text" in opt_res

        # 3. Retrieve
        get_resp = client.get(f"/api/optimize/{analysis_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["analysis_id"] == analysis_id

        # 4. Download PDF
        pdf_dl = client.get(f"/api/optimize/{analysis_id}/pdf")
        assert pdf_dl.status_code == 200
        assert pdf_dl.headers["content-type"] == "application/pdf"
        assert pdf_dl.content.startswith(b"%PDF")

        # 5. Download Report
        report_dl = client.get(f"/api/optimize/{analysis_id}/report")
        assert report_dl.status_code == 200
        assert report_dl.headers["content-type"] == "application/pdf"
        assert report_dl.content.startswith(b"%PDF")

        # 6. Download DOCX
        docx_dl = client.get(f"/api/optimize/{analysis_id}/docx")
        assert docx_dl.status_code == 200
        assert "openxmlformats" in docx_dl.headers["content-type"]
        assert docx_dl.content.startswith(b"PK")



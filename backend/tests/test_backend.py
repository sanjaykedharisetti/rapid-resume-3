"""
Backend test suite for Matchly AI.

Run unit tests (no NLP model required):
    pytest tests/ -v -m "not e2e"

Run full end-to-end tests (requires model download):
    pytest tests/ -v -m "e2e"

Run all tests:
    pytest tests/ -v
"""
from __future__ import annotations

import io
import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Ensure backend root is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ===========================================================================
# 1. Health endpoint
# ===========================================================================

@pytest.fixture
def client():
    """Create a TestClient with DB and model mocked."""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data


# ===========================================================================
# 2. Resume parser – PDF
# ===========================================================================

def _make_simple_pdf_bytes() -> bytes:
    """Create a minimal text-based PDF in memory using reportlab."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        c.drawString(72, 720, "John Doe – Software Engineer")
        c.drawString(72, 700, "Skills: Python, Machine Learning, SQL")
        c.drawString(72, 680, "Education: B.S. Computer Science, MIT 2020")
        c.save()
        buf.seek(0)
        return buf.read()
    except ImportError:
        pytest.skip("reportlab not installed – cannot create test PDF")


def test_pdf_extraction():
    from app.services.resume_parser import extract_text_from_bytes
    pdf_bytes = _make_simple_pdf_bytes()
    text = extract_text_from_bytes(pdf_bytes, "resume.pdf")
    assert "Python" in text or "John" in text  # basic smoke check


def test_pdf_extraction_scanned_fallback():
    """Minimal PDF with no text should raise ResumeParseError."""
    from app.services.resume_parser import ResumeParseError, extract_text_from_bytes
    try:
        import fitz
    except ImportError:
        pytest.skip("PyMuPDF not installed")

    # Create a PDF that genuinely has no text (just metadata)
    doc = fitz.open()
    doc.new_page()
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    pdf_bytes = buf.getvalue()

    with pytest.raises(ResumeParseError, match="No extractable text"):
        extract_text_from_bytes(pdf_bytes, "scanned.pdf")


# ===========================================================================
# 3. Resume parser – DOCX
# ===========================================================================

def _make_docx_bytes() -> bytes:
    try:
        from docx import Document
        doc = Document()
        doc.add_paragraph("Jane Smith – Data Scientist")
        doc.add_paragraph("Skills: Python, TensorFlow, SQL, Docker")
        doc.add_paragraph("Education: Master's in Data Science, Stanford 2021")
        doc.add_paragraph("Experience: 3 years of machine learning experience")
        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        return buf.read()
    except ImportError:
        pytest.skip("python-docx not installed")


def test_docx_extraction():
    from app.services.resume_parser import extract_text_from_bytes
    docx_bytes = _make_docx_bytes()
    text = extract_text_from_bytes(docx_bytes, "resume.docx")
    assert "Python" in text
    assert "Jane" in text


# ===========================================================================
# 4. Unsupported file formats
# ===========================================================================

def test_text_and_doc_formats_supported():
    from app.services.resume_parser import extract_text_from_bytes
    # 1. Plain text format
    txt_content = b"John Doe - Senior Software Engineer\nSkills: Python, SQL, Docker, AWS"
    txt_extracted = extract_text_from_bytes(txt_content, "resume.txt")
    assert "Python" in txt_extracted
    assert "John Doe" in txt_extracted

    # 2. Markdown format
    md_content = b"# John Doe\n## Experience\nFull Stack Developer with Python and React"
    md_extracted = extract_text_from_bytes(md_content, "resume.md")
    assert "Full Stack" in md_extracted

    # 3. HTML format
    html_content = b"<html><body><h1>Jane Smith</h1><p>Data Scientist with Python and SQL</p></body></html>"
    html_extracted = extract_text_from_bytes(html_content, "resume.html")
    assert "Jane Smith" in html_extracted

    # 4. RTF format
    rtf_content = b"{\\rtf1\\ansi Jane Smith\\par Senior Engineer with Python skills}"
    rtf_extracted = extract_text_from_bytes(rtf_content, "resume.rtf")
    assert "Jane Smith" in rtf_extracted


def test_unsupported_or_empty_binary_fails():
    from app.services.resume_parser import ResumeParseError, extract_text_from_bytes
    with pytest.raises(ResumeParseError):
        extract_text_from_bytes(b"\x00\x00\x00\x00\x00\x00\x00", "corrupted.bin")

    with pytest.raises(ResumeParseError):
        extract_text_from_bytes(b"", "empty.txt")



# ===========================================================================
# 5. Skill extraction
# ===========================================================================

def test_skill_extraction_basic():
    from app.services.skill_extractor import extract_skills
    text = "I have 3 years of Python experience and work with React and SQL databases."
    skills = extract_skills(text)
    assert "Python" in skills
    assert "React" in skills
    assert "SQL" in skills


def test_java_not_matched_in_javascript():
    """Critical: 'Java' must NOT be extracted when only 'JavaScript' appears."""
    from app.services.skill_extractor import extract_skills
    text = "I am an expert JavaScript developer. I use JavaScript every day."
    skills = extract_skills(text)
    assert "JavaScript" in skills
    assert "Java" not in skills, "Java must not match inside 'JavaScript'"


def test_java_matched_standalone():
    """'Java' should be extracted when it appears as a standalone word."""
    from app.services.skill_extractor import extract_skills
    text = "Backend developer with Java and Spring Boot experience."
    skills = extract_skills(text)
    assert "Java" in skills


def test_java_and_javascript_together():
    """Both Java and JavaScript should be found when both appear."""
    from app.services.skill_extractor import extract_skills
    text = "I know Java, JavaScript, and Python."
    skills = extract_skills(text)
    assert "Java" in skills
    assert "JavaScript" in skills


def test_skill_aliases():
    """Test that common aliases map to canonical names."""
    from app.services.skill_extractor import extract_skills
    text = "Experience with sklearn, numpy, reactjs and k8s."
    skills = extract_skills(text)
    assert "Scikit-learn" in skills
    assert "NumPy" in skills
    assert "React" in skills
    assert "Kubernetes" in skills


def test_empty_text_returns_empty():
    from app.services.skill_extractor import extract_skills
    assert extract_skills("") == []
    assert extract_skills("   ") == []


# ===========================================================================
# 6. Semantic score range (mocked model)
# ===========================================================================

def test_semantic_score_range_with_mock():
    """Test that the semantic score is always in [0, 1]."""
    from app.services import semantic_matcher

    with patch.object(semantic_matcher, "_model_ready", True), \
         patch.object(semantic_matcher, "_model") as mock_model:

        import numpy as np
        # Simulate two orthogonal vectors (similarity = 0)
        mock_model.encode.return_value = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ])
        score = semantic_matcher.compute_semantic_similarity("text a", "text b")
        assert score is not None
        assert 0.0 <= score <= 1.0

        # Simulate identical vectors (similarity = 1)
        mock_model.encode.return_value = np.array([
            [1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
        ])
        score = semantic_matcher.compute_semantic_similarity("same", "same")
        assert score is not None
        assert abs(score - 1.0) < 1e-6


def test_semantic_fallback_when_model_not_ready():
    """When model is not ready, compute_semantic_similarity returns None."""
    from app.services import semantic_matcher
    with patch.object(semantic_matcher, "_model_ready", False):
        result = semantic_matcher.compute_semantic_similarity("a", "b")
        assert result is None


def test_tfidf_fallback():
    from app.services.semantic_matcher import compute_tfidf_similarity
    score = compute_tfidf_similarity(
        "Python machine learning data science",
        "Python data scientist machine learning engineer",
    )
    assert 0.0 <= score <= 1.0
    assert score > 0.3  # Should be reasonably similar


# ===========================================================================
# 7. Final score calculation
# ===========================================================================

def test_score_clamped_between_0_and_100():
    from app.services.scoring_service import compute_score

    # Mock semantic matcher to return a high score
    with patch("app.services.scoring_service.semantic_matcher.compute_semantic_similarity", return_value=1.0):
        result = compute_score(
            resume_text="Python Java SQL Machine Learning Docker AWS React",
            job_description="We need Python Java SQL Machine Learning Docker AWS React developer",
        )
        assert 0 <= result.overall_score <= 100


def test_score_not_random():
    """Same inputs should produce same score."""
    from app.services.scoring_service import compute_score

    with patch("app.services.scoring_service.semantic_matcher.compute_semantic_similarity", return_value=0.7):
        result1 = compute_score("Python developer with SQL skills", "Python SQL engineer")
        result2 = compute_score("Python developer with SQL skills", "Python SQL engineer")
        assert result1.overall_score == result2.overall_score


def test_missing_required_skills_in_result():
    from app.services.scoring_service import compute_score

    with patch("app.services.scoring_service.semantic_matcher.compute_semantic_similarity", return_value=0.5):
        result = compute_score(
            resume_text="I am a Python developer",
            job_description="Looking for Python, Docker, Kubernetes, AWS developer",
        )
        # Docker/Kubernetes/AWS should appear as missing (not in resume)
        missing_lower = [s.lower() for s in result.missing_required_skills]
        assert any("docker" in s for s in missing_lower) or len(result.missing_required_skills) > 0


def test_score_category():
    from app.services.scoring_service import score_to_category
    assert score_to_category(85) == "Strong Match"
    assert score_to_category(65) == "Good Match"
    assert score_to_category(45) == "Moderate Match"
    assert score_to_category(20) == "Low Match"


# ===========================================================================
# 8. Empty job description / resume handling via API
# ===========================================================================

def test_empty_job_description_rejected(client):
    import io as _io
    pdf_bytes = _make_simple_pdf_bytes()
    response = client.post(
        "/api/analyze",
        data={"job_description": ""},
        files={"resume": ("resume.pdf", _io.BytesIO(pdf_bytes), "application/pdf")},
    )
    assert response.status_code in (400, 422)


def test_invalid_file_type_rejected(client):
    response = client.post(
        "/api/analyze",
        data={"job_description": "We need a Python developer with 3 years of experience"},
        files={"resume": ("resume.txt", io.BytesIO(b"some content"), "text/plain")},
    )
    assert response.status_code in (415, 422)


# ===========================================================================
# 9. API response structure
# ===========================================================================

REQUIRED_FIELDS = [
    "analysis_id", "filename", "overall_score", "match_category",
    "semantic_similarity_score", "skill_matching_score",
    "qualification_matching_score", "experience_relevance_score",
    "matched_skills", "missing_required_skills", "missing_preferred_skills",
    "additional_skills", "required_skill_coverage",
    "resume_qualifications", "job_qualifications",
    "resume_experience", "job_experience_requirements",
    "important_keywords", "missing_keywords",
    "improvement_suggestions", "limitations",
]


@pytest.mark.e2e
def test_analyze_api_response_structure(client):
    """
    End-to-end test: requires all dependencies installed.
    Run with: pytest tests/ -v -m e2e
    """
    pdf_bytes = _make_simple_pdf_bytes()
    jd = (
        "We are looking for a Python developer with experience in Machine Learning, "
        "SQL, Docker, and AWS. Bachelor's degree required. 3+ years of experience."
    )
    response = client.post(
        "/api/analyze",
        data={"job_description": jd},
        files={"resume": ("resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    assert response.status_code == 200, response.text
    data = response.json()

    for field in REQUIRED_FIELDS:
        assert field in data, f"Missing field: {field}"

    assert 0 <= data["overall_score"] <= 100
    assert data["match_category"] in ("Strong Match", "Good Match", "Moderate Match", "Low Match")
    assert isinstance(data["matched_skills"], list)
    assert isinstance(data["improvement_suggestions"], list)


# ===========================================================================
# 10. Database history operations
# ===========================================================================

@pytest.mark.e2e
def test_history_list(client):
    response = client.get("/api/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.e2e
def test_history_delete(client):
    """Submit an analysis and then delete it."""
    pdf_bytes = _make_simple_pdf_bytes()
    jd = "Python developer with 2 years of experience required."
    # Create record
    resp = client.post(
        "/api/analyze",
        data={"job_description": jd},
        files={"resume": ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    assert resp.status_code == 200
    aid = resp.json()["analysis_id"]

    # Delete
    del_resp = client.delete(f"/api/history/{aid}")
    assert del_resp.status_code == 204

    # Confirm deleted
    get_resp = client.get(f"/api/history/{aid}")
    assert get_resp.status_code == 404

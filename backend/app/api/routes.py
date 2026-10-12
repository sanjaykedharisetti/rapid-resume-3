"""
FastAPI route handlers for the Resume-Job Matcher & AI Resume Optimizer API.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database import get_db
from app.models.analysis import AnalysisRecord, OptimizationRecord
from app.schemas.analysis import (
    AnalysisResponse,
    HealthResponse,
    HistoryDetailResponse,
    HistoryListItem,
    ReadinessResponse,
)
from app.schemas.optimization import (
    ComponentScoreDetail,
    OptimizeRequest,
    OptimizeResponse,
)
from app.services import semantic_matcher
from app.services.pdf_generator import (
    generate_ats_optimization_report_pdf,
    generate_optimized_resume_docx,
    generate_optimized_resume_pdf,
)
from app.services.report_service import generate_pdf_report
from app.services.resume_optimizer import optimize_resume
from app.services.resume_parser import ResumeParseError, extract_text_from_bytes
from app.services.scoring_service import compute_score
from app.services.text_processor import clean_text

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


# ---------------------------------------------------------------------------
# Health endpoints
# ---------------------------------------------------------------------------

@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Return basic service health status."""
    return HealthResponse(
        status="ok",
        environment=settings.APP_ENV,
    )


@router.get("/health/ready", response_model=ReadinessResponse, tags=["Health"])
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Check whether all services are ready:
    - NLP model loaded
    - Database accessible
    """
    db_ready = False
    db_error = ""
    try:
        await db.execute(select(AnalysisRecord).limit(1))
        db_ready = True
    except Exception as exc:
        db_error = str(exc)

    nlp_ready = semantic_matcher.is_model_ready()
    model_error = semantic_matcher.get_model_error() if not nlp_ready else ""

    all_ready = db_ready  # NLP model may fall back to TF-IDF; DB is required

    details_parts = []
    if not nlp_ready:
        details_parts.append(f"NLP model not ready: {model_error}. TF-IDF fallback will be used.")
    if not db_ready:
        details_parts.append(f"Database not ready: {db_error}")

    return ReadinessResponse(
        status="ready" if all_ready else "not_ready",
        nlp_model_ready=nlp_ready,
        database_ready=db_ready,
        details="; ".join(details_parts) if details_parts else None,
    )


# ---------------------------------------------------------------------------
# Analyze endpoint
# ---------------------------------------------------------------------------

@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    tags=["Analysis"],
)
async def analyze_resume(
    resume: UploadFile = File(..., description="Resume file (PDF or DOCX)"),
    job_description: str = Form(..., description="Job description text"),
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze a resume against a job description and return a compatibility score.
    """
    # ---- Validation -------------------------------------------------------

    if not job_description or not job_description.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Job description cannot be empty.",
        )

    if len(job_description.strip()) < 50:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Job description is too short. Please provide a complete job description.",
        )

    filename = resume.filename or "resume"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{ext}'. Please upload a PDF or DOCX file.",
        )

    content_type = resume.content_type or ""
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        logger.warning(
            "Unexpected content-type '%s' for file '%s'; proceeding with extension check.",
            content_type, filename,
        )

    file_bytes = await resume.read()

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file is empty.",
        )

    if len(file_bytes) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB} MB.",
        )

    # ---- Text extraction --------------------------------------------------

    try:
        raw_text = extract_text_from_bytes(file_bytes, filename)
    except ResumeParseError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception("Unexpected error parsing resume '%s'", filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while parsing the resume.",
        )

    # ---- Text cleaning ----------------------------------------------------

    resume_text = clean_text(raw_text)
    jd_text = clean_text(job_description)

    if len(resume_text) < 20:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Not enough text could be extracted from the resume.",
        )

    # ---- Scoring ----------------------------------------------------------

    try:
        result = compute_score(resume_text, jd_text)
    except Exception as exc:
        logger.exception("Error computing score for '%s'", filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during analysis. Please try again.",
        )

    # ---- Persist to database ----------------------------------------------

    analysis_id = str(uuid.uuid4())
    response_dict = {
        "analysis_id": analysis_id,
        "filename": filename,
        "overall_score": result.overall_score,
        "match_category": result.match_category,
        "semantic_similarity_score": result.semantic_similarity_score,
        "skill_matching_score": result.skill_matching_score,
        "qualification_matching_score": result.qualification_matching_score,
        "experience_relevance_score": result.experience_relevance_score,
        "matched_skills": result.matched_skills,
        "missing_required_skills": result.missing_required_skills,
        "missing_preferred_skills": result.missing_preferred_skills,
        "additional_skills": result.additional_skills,
        "required_skill_coverage": result.required_skill_coverage,
        "resume_qualifications": result.resume_qualifications,
        "job_qualifications": result.job_qualifications,
        "qualification_notes": result.qualification_notes,
        "resume_experience": result.resume_experience,
        "job_experience_requirements": result.job_experience_requirements,
        "experience_notes": result.experience_notes,
        "important_keywords": result.important_keywords,
        "missing_keywords": result.missing_keywords,
        "improvement_suggestions": result.improvement_suggestions,
        "limitations": result.limitations,
    }

    try:
        record = AnalysisRecord(
            id=analysis_id,
            filename=filename,
            overall_score=result.overall_score,
            match_category=result.match_category,
            resume_text=resume_text,
            job_description=jd_text,
            semantic_similarity_score=result.semantic_similarity_score,
            skill_matching_score=result.skill_matching_score,
            qualification_matching_score=result.qualification_matching_score,
            experience_relevance_score=result.experience_relevance_score,
            matched_skill_count=len(result.matched_skills),
            required_skill_count=len(result.matched_skills) + len(result.missing_required_skills),
            missing_required_count=len(result.missing_required_skills),
        )
        record.set_full_result(response_dict)
        db.add(record)
        await db.commit()
        await db.refresh(record)
    except Exception as exc:
        logger.error("Failed to save analysis record: %s", exc)

    return AnalysisResponse(**response_dict)


# ---------------------------------------------------------------------------
# Resume Optimization Endpoints
# ---------------------------------------------------------------------------

@router.post("/optimize", response_model=OptimizeResponse, tags=["Optimization"])
async def run_resume_optimization(
    payload: OptimizeRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Run iterative AI resume optimization against target job description.
    Recalculates real ATS scores without hardcoding or hallucinations.
    """
    if not payload.analysis_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="analysis_id is required to optimize resume.",
        )

    # 1. Fetch original analysis record
    result = await db.execute(
        select(AnalysisRecord).where(AnalysisRecord.id == payload.analysis_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Original analysis record not found.",
        )

    resume_text = record.resume_text
    job_description = record.job_description

    # Fallback to full_result if resume_text/job_description wasn't stored separately
    if not resume_text or not job_description:
        full = record.get_full_result()
        if full and "resume_text" in full:
            resume_text = full.get("resume_text")
            job_description = full.get("job_description")

    if not resume_text or not job_description:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Resume text or job description missing from analysis session. Please analyze again.",
        )

    # 2. Run optimization engine
    try:
        opt_data = optimize_resume(
            original_text=resume_text,
            job_description=job_description,
            target_score=payload.target_score,
            max_iterations=payload.iterations,
        )
    except Exception as exc:
        logger.exception("Resume optimization failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization engine encountered an error: {str(exc)}",
        )

    optimization_id = str(uuid.uuid4())
    now_utc = datetime.now(timezone.utc)

    opt_data["optimization_id"] = optimization_id
    opt_data["analysis_id"] = record.id
    opt_data["filename"] = record.filename
    opt_data["created_at"] = now_utc

    # 3. Store in DB
    try:
        opt_record = OptimizationRecord(
            id=optimization_id,
            analysis_id=record.id,
            filename=record.filename,
            original_score=opt_data["original_score"],
            optimized_score=opt_data["optimized_score"],
            score_improvement=opt_data["score_improvement"],
            target_score=payload.target_score,
            target_reached=opt_data["target_reached"],
            summary=opt_data["status_message"],
            optimized_resume_text=opt_data["optimized_resume_text"],
        )
        opt_record.set_data(opt_data)
        db.add(opt_record)

        # Update analysis record
        record.optimized_score = opt_data["optimized_score"]
        record.optimization_summary = opt_data["status_message"]
        await db.commit()
    except Exception as exc:
        logger.error("Failed to store optimization record: %s", exc)

    return OptimizeResponse(
        optimization_id=optimization_id,
        analysis_id=record.id,
        filename=record.filename,
        original_score=opt_data["original_score"],
        optimized_score=opt_data["optimized_score"],
        score_improvement=opt_data["score_improvement"],
        target_score=opt_data["target_score"],
        target_reached=opt_data["target_reached"],
        status_message=opt_data["status_message"],
        component_scores_before=ComponentScoreDetail(**opt_data["component_scores_before"]),
        component_scores_after=ComponentScoreDetail(**opt_data["component_scores_after"]),
        matched_skills_before=opt_data["matched_skills_before"],
        matched_skills_after=opt_data["matched_skills_after"],
        newly_matched_skills=opt_data["newly_matched_skills"],
        remaining_missing_skills=opt_data["remaining_missing_skills"],
        missing_preferred_skills=opt_data["missing_preferred_skills"],
        missing_keywords=opt_data["missing_keywords"],
        formatting_issues=opt_data["formatting_issues"],
        summary_of_changes=opt_data["summary_of_changes"],
        unanswered_questions=opt_data["unanswered_questions"],
        remaining_gaps=opt_data["remaining_gaps"],
        original_resume_text=opt_data["original_resume_text"],
        optimized_resume_text=opt_data["optimized_resume_text"],
        original_sections=opt_data["original_sections"],
        optimized_sections=opt_data["optimized_sections"],
        iterations_run=opt_data["iterations_run"],
        created_at=now_utc,
    )


@router.get("/optimize/{analysis_id}", response_model=OptimizeResponse, tags=["Optimization"])
async def get_optimization_detail(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Fetch saved optimization results for an analysis session."""
    result = await db.execute(
        select(OptimizationRecord)
        .where(OptimizationRecord.analysis_id == analysis_id)
        .order_by(OptimizationRecord.created_at.desc())
    )
    opt_record = result.scalars().first()
    if not opt_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No optimization record found for this analysis.",
        )

    data = opt_record.get_data()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Optimization detail payload is empty.",
        )

    data["optimization_id"] = opt_record.id
    data["created_at"] = opt_record.created_at
    return OptimizeResponse(
        optimization_id=opt_record.id,
        analysis_id=opt_record.analysis_id,
        filename=opt_record.filename,
        original_score=data["original_score"],
        optimized_score=data["optimized_score"],
        score_improvement=data["score_improvement"],
        target_score=data.get("target_score", 85.0),
        target_reached=data.get("target_reached", False),
        status_message=data.get("status_message", ""),
        component_scores_before=ComponentScoreDetail(**data["component_scores_before"]),
        component_scores_after=ComponentScoreDetail(**data["component_scores_after"]),
        matched_skills_before=data.get("matched_skills_before", []),
        matched_skills_after=data.get("matched_skills_after", []),
        newly_matched_skills=data.get("newly_matched_skills", []),
        remaining_missing_skills=data.get("remaining_missing_skills", []),
        missing_preferred_skills=data.get("missing_preferred_skills", []),
        missing_keywords=data.get("missing_keywords", []),
        formatting_issues=data.get("formatting_issues", []),
        summary_of_changes=data.get("summary_of_changes", []),
        unanswered_questions=data.get("unanswered_questions", []),
        remaining_gaps=data.get("remaining_gaps", []),
        original_resume_text=data.get("original_resume_text", ""),
        optimized_resume_text=data.get("optimized_resume_text", ""),
        original_sections=data.get("original_sections", {}),
        optimized_sections=data.get("optimized_sections", {}),
        iterations_run=data.get("iterations_run", 1),
        created_at=opt_record.created_at,
    )


@router.get("/optimize/{analysis_id}/pdf", tags=["Optimization"])
async def download_optimized_resume_pdf(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Download clean, ATS-compliant optimized resume PDF (ready for employers)."""
    result = await db.execute(
        select(OptimizationRecord)
        .where(OptimizationRecord.analysis_id == analysis_id)
        .order_by(OptimizationRecord.created_at.desc())
    )
    opt_record = result.scalars().first()
    if not opt_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No optimization record found for this analysis.",
        )

    data = opt_record.get_data()
    try:
        pdf_bytes = generate_optimized_resume_pdf(data, filename=opt_record.filename)
    except Exception as exc:
        logger.error("Failed to generate optimized resume PDF: %s", exc)
        raise HTTPException(
            status_code=500, detail="Failed to generate optimized resume PDF."
        )

    safe_name = opt_record.filename.replace(" ", "_").replace(".pdf", "").replace(".docx", "")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="optimized_resume_{safe_name}.pdf"',
        },
    )


@router.get("/optimize/{analysis_id}/report", tags=["Optimization"])
async def download_ats_optimization_report(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Download full ATS optimization report PDF with before/after score breakdown."""
    result = await db.execute(
        select(OptimizationRecord)
        .where(OptimizationRecord.analysis_id == analysis_id)
        .order_by(OptimizationRecord.created_at.desc())
    )
    opt_record = result.scalars().first()
    if not opt_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No optimization record found for this analysis.",
        )

    data = opt_record.get_data()
    try:
        report_bytes = generate_ats_optimization_report_pdf(data, filename=opt_record.filename)
    except Exception as exc:
        logger.error("Failed to generate ATS report PDF: %s", exc)
        raise HTTPException(
            status_code=500, detail="Failed to generate ATS report PDF."
        )

    safe_name = opt_record.filename.replace(" ", "_").replace(".pdf", "").replace(".docx", "")
    return Response(
        content=report_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="ats_report_{safe_name}.pdf"',
        },
    )


@router.get("/optimize/{analysis_id}/docx", tags=["Optimization"])
async def download_optimized_resume_docx(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Download editable Word (.docx) document matching optimized resume."""
    result = await db.execute(
        select(OptimizationRecord)
        .where(OptimizationRecord.analysis_id == analysis_id)
        .order_by(OptimizationRecord.created_at.desc())
    )
    opt_record = result.scalars().first()
    if not opt_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No optimization record found for this analysis.",
        )

    data = opt_record.get_data()
    try:
        docx_bytes = generate_optimized_resume_docx(data, filename=opt_record.filename)
    except Exception as exc:
        logger.error("Failed to generate DOCX resume: %s", exc)
        raise HTTPException(
            status_code=500, detail="Failed to generate editable DOCX resume."
        )

    safe_name = opt_record.filename.replace(" ", "_").replace(".pdf", "").replace(".docx", "")
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="optimized_resume_{safe_name}.docx"',
        },
    )


# ---------------------------------------------------------------------------
# History endpoints
# ---------------------------------------------------------------------------

@router.get("/history", response_model=List[HistoryListItem], tags=["History"])
async def get_history(db: AsyncSession = Depends(get_db)):
    """Return list of previous analysis records (metadata only)."""
    result = await db.execute(
        select(AnalysisRecord).order_by(AnalysisRecord.created_at.desc()).limit(100)
    )
    records = result.scalars().all()
    return [
        HistoryListItem(
            analysis_id=r.id,
            filename=r.filename,
            overall_score=r.overall_score,
            match_category=r.match_category,
            matched_skill_count=r.matched_skill_count,
            required_skill_count=r.required_skill_count,
            created_at=r.created_at,
        )
        for r in records
    ]


@router.get("/history/{analysis_id}", response_model=HistoryDetailResponse, tags=["History"])
async def get_history_detail(analysis_id: str, db: AsyncSession = Depends(get_db)):
    """Return full analysis detail for a specific record."""
    result = await db.execute(
        select(AnalysisRecord).where(AnalysisRecord.id == analysis_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis record not found.")

    full = record.get_full_result()
    if not full:
        raise HTTPException(status_code=404, detail="Analysis detail data not found.")

    full["created_at"] = record.created_at
    return HistoryDetailResponse(**full)


@router.delete("/history/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["History"])
async def delete_history(analysis_id: str, db: AsyncSession = Depends(get_db)):
    """Delete an analysis record."""
    result = await db.execute(
        select(AnalysisRecord).where(AnalysisRecord.id == analysis_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis record not found.")

    await db.delete(record)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Legacy Report download
# ---------------------------------------------------------------------------

@router.get("/history/{analysis_id}/report", tags=["History"])
async def download_report(analysis_id: str, db: AsyncSession = Depends(get_db)):
    """Generate and download a PDF report for an analysis."""
    result = await db.execute(
        select(AnalysisRecord).where(AnalysisRecord.id == analysis_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis record not found.")

    full = record.get_full_result()
    if not full:
        raise HTTPException(status_code=404, detail="Analysis detail not available.")

    try:
        pdf_bytes = generate_pdf_report(full, filename=record.filename)
    except Exception as exc:
        logger.error("PDF generation failed: %s", exc)
        raise HTTPException(
            status_code=500, detail="Failed to generate PDF report."
        )

    safe_name = record.filename.replace(" ", "_").replace(".pdf", "").replace(".docx", "")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="matchly_report_{safe_name}.pdf"',
        },
    )

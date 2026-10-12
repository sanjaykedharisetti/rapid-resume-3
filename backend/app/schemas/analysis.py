"""
Pydantic schemas for request/response validation.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Analysis response
# ---------------------------------------------------------------------------

class AnalysisResponse(BaseModel):
    analysis_id: str
    filename: str
    overall_score: float = Field(ge=0, le=100)
    match_category: str  # "Strong Match" | "Good Match" | "Moderate Match" | "Low Match"

    # Component scores (0–100)
    semantic_similarity_score: float
    skill_matching_score: float
    qualification_matching_score: float
    experience_relevance_score: float

    # Skills
    matched_skills: List[str]
    missing_required_skills: List[str]
    missing_preferred_skills: List[str]
    additional_skills: List[str]
    required_skill_coverage: float  # 0–100 %

    # Qualifications
    resume_qualifications: List[str]
    job_qualifications: List[str]
    qualification_notes: Optional[str] = None

    # Experience
    resume_experience: List[str]
    job_experience_requirements: List[str]
    experience_notes: Optional[str] = None

    # Keywords
    important_keywords: List[str]
    missing_keywords: List[str]

    # Suggestions
    improvement_suggestions: List[str]

    # Transparency
    limitations: List[str]


# ---------------------------------------------------------------------------
# History schemas
# ---------------------------------------------------------------------------

class HistoryListItem(BaseModel):
    analysis_id: str
    filename: str
    overall_score: float
    match_category: str
    matched_skill_count: int
    required_skill_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class HistoryDetailResponse(AnalysisResponse):
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Health schemas
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
    environment: str


class ReadinessResponse(BaseModel):
    status: str
    nlp_model_ready: bool
    database_ready: bool
    details: Optional[str] = None

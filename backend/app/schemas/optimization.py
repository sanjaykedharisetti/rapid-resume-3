"""
Pydantic schemas for resume optimization request and response models.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OptimizeRequest(BaseModel):
    analysis_id: Optional[str] = Field(None, description="ID of previously analyzed resume")
    target_score: float = Field(85.0, ge=50.0, le=100.0, description="Target ATS compatibility score")
    iterations: int = Field(3, ge=1, le=5, description="Maximum iterative refinement loops")


class ComponentScoreDetail(BaseModel):
    semantic_similarity_score: float = Field(..., ge=0, le=100)
    skill_matching_score: float = Field(..., ge=0, le=100)
    qualification_matching_score: float = Field(..., ge=0, le=100)
    experience_relevance_score: float = Field(..., ge=0, le=100)


class OptimizedSections(BaseModel):
    contact: Optional[str] = None
    summary: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    projects: Optional[str] = None
    education: Optional[str] = None
    certifications: Optional[str] = None
    other: Optional[str] = None


class OptimizeResponse(BaseModel):
    optimization_id: str
    analysis_id: str
    filename: str

    # Scores
    original_score: float = Field(..., ge=0, le=100)
    optimized_score: float = Field(..., ge=0, le=100)
    score_improvement: float
    target_score: float = 85.0
    target_reached: bool
    status_message: str

    # Component Scores
    component_scores_before: ComponentScoreDetail
    component_scores_after: ComponentScoreDetail

    # Skills comparison
    matched_skills_before: List[str]
    matched_skills_after: List[str]
    newly_matched_skills: List[str]
    remaining_missing_skills: List[str]
    missing_preferred_skills: List[str]
    missing_keywords: List[str]

    # Analysis & Transparency
    formatting_issues: List[str]
    summary_of_changes: List[str]
    unanswered_questions: List[str]
    remaining_gaps: List[str]

    # Full text & sections
    original_resume_text: str
    optimized_resume_text: str
    original_sections: Dict[str, str]
    optimized_sections: Dict[str, str]

    iterations_run: int
    created_at: datetime

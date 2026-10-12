"""
SQLAlchemy ORM models for analysis and resume optimization records.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    # Metadata
    filename: Mapped[str] = mapped_column(String(255))
    overall_score: Mapped[float] = mapped_column(Float)
    match_category: Mapped[str] = mapped_column(String(50))

    # Stored text for optimization
    resume_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    job_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Component scores
    semantic_similarity_score: Mapped[float] = mapped_column(Float, default=0.0)
    skill_matching_score: Mapped[float] = mapped_column(Float, default=0.0)
    qualification_matching_score: Mapped[float] = mapped_column(Float, default=0.0)
    experience_relevance_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Skill counts
    matched_skill_count: Mapped[int] = mapped_column(Integer, default=0)
    required_skill_count: Mapped[int] = mapped_column(Integer, default=0)
    missing_required_count: Mapped[int] = mapped_column(Integer, default=0)

    # Full JSON result stored for history detail view
    full_result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Optimization reference
    optimized_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    optimization_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def set_full_result(self, data: dict) -> None:
        self.full_result = json.dumps(data)

    def get_full_result(self) -> dict | None:
        if self.full_result:
            return json.loads(self.full_result)
        return None


class OptimizationRecord(Base):
    __tablename__ = "optimization_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    filename: Mapped[str] = mapped_column(String(255))
    original_score: Mapped[float] = mapped_column(Float)
    optimized_score: Mapped[float] = mapped_column(Float)
    score_improvement: Mapped[float] = mapped_column(Float)
    target_score: Mapped[float] = mapped_column(Float, default=85.0)
    target_reached: Mapped[bool] = mapped_column(Boolean, default=False)

    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    optimized_resume_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    full_optimization_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def set_data(self, data: dict) -> None:
        def _default(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        self.full_optimization_data = json.dumps(data, default=_default)

    def get_data(self) -> dict | None:
        if self.full_optimization_data:
            return json.loads(self.full_optimization_data)
        return None

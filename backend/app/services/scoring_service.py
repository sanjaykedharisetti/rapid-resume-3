"""
Scoring service: assembles all component scores into a final match score.

Weighting (configurable):
  Semantic similarity    : 40%
  Skill matching         : 35%
  Qualification matching : 15%
  Experience relevance   : 10%

If a component cannot be evaluated, the remaining weights are re-normalised
proportionally so the final score is still on a 0–100 scale.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from app.services import semantic_matcher, skill_extractor
from app.services.text_processor import extract_sections, get_section_text

logger = logging.getLogger(__name__)

# Default weights
DEFAULT_WEIGHTS: Dict[str, float] = {
    "semantic": 0.40,
    "skill": 0.35,
    "qualification": 0.15,
    "experience": 0.10,
}

MATCH_THRESHOLDS = {
    "Strong Match": 75,
    "Good Match": 55,
    "Moderate Match": 35,
    "Low Match": 0,
}


def score_to_category(score: float) -> str:
    if score >= 75:
        return "Strong Match"
    if score >= 55:
        return "Good Match"
    if score >= 35:
        return "Moderate Match"
    return "Low Match"


# ---------------------------------------------------------------------------
# Qualification helpers
# ---------------------------------------------------------------------------

DEGREE_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("PhD / Doctorate", re.compile(r"\b(ph\.?d|doctorate|doctoral)\b", re.I)),
    ("Master's Degree", re.compile(r"\b(master'?s?|m\.?s\.?|m\.?tech\.?|m\.?e\.?|mba|m\.?sc\.?|m\.?eng\.?)\b", re.I)),
    ("Bachelor's Degree", re.compile(r"\b(bachelor'?s?|b\.?s\.?|b\.?tech\.?|b\.?e\.?|b\.?sc\.?|b\.?eng\.?|undergraduate)\b", re.I)),
    ("Associate Degree", re.compile(r"\b(associate'?s?|a\.?s\.?|a\.?a\.?)\b", re.I)),
    ("High School / GED", re.compile(r"\b(high school|ged|secondary)\b", re.I)),
]

CERT_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("AWS Certified", re.compile(r"\baws\s+certif", re.I)),
    ("Google Cloud Certified", re.compile(r"\bgoogle\s+cloud\s+certif", re.I)),
    ("Azure Certified", re.compile(r"\bazure\s+certif", re.I)),
    ("PMP", re.compile(r"\bpmp\b", re.I)),
    ("Certified Scrum Master", re.compile(r"\b(csm|certified\s+scrum)\b", re.I)),
    ("CISSP", re.compile(r"\bcissp\b", re.I)),
    ("CPA", re.compile(r"\bcpa\b", re.I)),
]


def _extract_qualifications(text: str) -> List[str]:
    found: List[str] = []
    for label, pattern in DEGREE_PATTERNS + CERT_PATTERNS:
        if pattern.search(text):
            found.append(label)
    return found


def _qualify_score(resume_quals: List[str], job_quals: List[str]) -> Tuple[float, str]:
    """
    Score qualification match.
    Returns (score 0-100, notes string).
    """
    if not job_quals:
        return 50.0, "No specific qualifications were identified in the job description. Score defaulted to 50."

    if not resume_quals:
        return 20.0, (
            "Qualifications were not clearly identified in the resume. "
            "This may be a parsing limitation. Defaulted to 20 — not a confirmed absence."
        )

    matched = set(resume_quals) & set(job_quals)
    coverage = len(matched) / len(job_quals) * 100
    notes = (
        f"{len(matched)} of {len(job_quals)} required qualifications identified "
        f"in the resume. Note: qualification matching is based on keyword detection "
        f"and may not be fully accurate."
    )
    return min(100.0, coverage), notes


# ---------------------------------------------------------------------------
# Experience helpers
# ---------------------------------------------------------------------------

YEARS_PATTERN = re.compile(
    r"(\d+)\s*(?:\+\s*)?(?:to\s*\d+\s*)?(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)?",
    re.I,
)


def _extract_experience_mentions(text: str) -> List[str]:
    """Extract sentences that mention experience, years, roles."""
    sentences: List[str] = []
    for sent in re.split(r"[.\n]", text):
        sent = sent.strip()
        if not sent:
            continue
        if re.search(r"\b(experience|year|worked|position|role|responsible)\b", sent, re.I):
            sentences.append(sent[:200])  # cap length
    return sentences[:10]  # return at most 10


def _experience_score(resume_text: str, job_text: str) -> Tuple[float, str]:
    """
    Estimate experience relevance.
    Returns (score 0-100, notes).
    """
    job_years_matches = YEARS_PATTERN.findall(job_text)
    resume_years_matches = YEARS_PATTERN.findall(resume_text)

    notes_parts: List[str] = []

    if not job_years_matches:
        notes_parts.append("No explicit experience requirements (years) were detected in the job description.")
        base_score = 50.0
    else:
        required_years = max(int(y) for y in job_years_matches)
        notes_parts.append(f"Job description appears to require approximately {required_years}+ years of experience.")

        if resume_years_matches:
            resume_years = max(int(y) for y in resume_years_matches)
            notes_parts.append(f"Resume mentions approximately {resume_years} years.")
            ratio = min(1.0, resume_years / required_years) if required_years > 0 else 1.0
            base_score = ratio * 100
        else:
            notes_parts.append(
                "No explicit years of experience were detected in the resume. "
                "This may be a parsing limitation, not a confirmed deficit."
            )
            base_score = 30.0  # Cautious fallback

    notes = " ".join(notes_parts)
    return min(100.0, base_score), notes


# ---------------------------------------------------------------------------
# Keyword helpers
# ---------------------------------------------------------------------------

STOPWORDS = {
    "the", "and", "for", "with", "this", "that", "from", "have", "will",
    "your", "our", "are", "was", "were", "been", "being", "not", "but",
    "can", "should", "would", "could", "may", "also", "such", "any",
    "all", "each", "more", "than", "into", "within", "about", "their",
    "they", "you", "we", "us", "he", "she", "it", "its", "an", "a",
    "is", "in", "on", "at", "to", "of", "or", "as", "by", "up",
}


def _extract_keywords(text: str, top_n: int = 30) -> List[str]:
    """Extract important keywords using simple TF-weighting on cleaned tokens."""
    tokens = re.findall(r"\b[a-zA-Z][a-zA-Z0-9\+\#\./]*\b", text)
    freq: Dict[str, int] = {}
    for tok in tokens:
        lower = tok.lower()
        if lower in STOPWORDS or len(lower) < 3:
            continue
        freq[lower] = freq.get(lower, 0) + 1

    sorted_tokens = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [tok for tok, _ in sorted_tokens[:top_n]]


# ---------------------------------------------------------------------------
# Main scoring function
# ---------------------------------------------------------------------------

@dataclass
class ScoreResult:
    overall_score: float
    match_category: str
    semantic_similarity_score: float
    skill_matching_score: float
    qualification_matching_score: float
    experience_relevance_score: float

    matched_skills: List[str] = field(default_factory=list)
    missing_required_skills: List[str] = field(default_factory=list)
    missing_preferred_skills: List[str] = field(default_factory=list)
    additional_skills: List[str] = field(default_factory=list)
    required_skill_coverage: float = 0.0

    resume_qualifications: List[str] = field(default_factory=list)
    job_qualifications: List[str] = field(default_factory=list)
    qualification_notes: str = ""

    resume_experience: List[str] = field(default_factory=list)
    job_experience_requirements: List[str] = field(default_factory=list)
    experience_notes: str = ""

    important_keywords: List[str] = field(default_factory=list)
    missing_keywords: List[str] = field(default_factory=list)

    improvement_suggestions: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)


def compute_score(
    resume_text: str,
    job_description: str,
    weights: Optional[Dict[str, float]] = None,
) -> ScoreResult:
    """
    Full scoring pipeline.
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS.copy()

    limitations: List[str] = []
    component_scores: Dict[str, Optional[float]] = {}

    # ------------------------------------------------------------------
    # 1. Semantic similarity
    # ------------------------------------------------------------------
    sem_raw = semantic_matcher.compute_semantic_similarity(resume_text, job_description)
    if sem_raw is None:
        # Fallback to TF-IDF
        sem_raw = semantic_matcher.compute_tfidf_similarity(resume_text, job_description)
        limitations.append(
            "Semantic model (all-MiniLM-L6-v2) was not available. "
            "TF-IDF cosine similarity was used as a fallback for the semantic component."
        )
    semantic_score = round(sem_raw * 100, 2)
    component_scores["semantic"] = semantic_score

    # ------------------------------------------------------------------
    # 2. Skill matching
    # ------------------------------------------------------------------
    resume_skills = set(skill_extractor.extract_skills(resume_text))
    job_skills_all = set(skill_extractor.extract_skills(job_description))

    # Heuristic: classify skills as required vs preferred based on JD keywords
    required_signals = re.compile(
        r"\b(required|must have|must-have|mandatory|essential|need|needs)\b", re.I
    )
    preferred_signals = re.compile(
        r"\b(preferred|nice to have|nice-to-have|optional|bonus|plus|desired)\b", re.I
    )

    job_required_skills: set[str] = set()
    job_preferred_skills: set[str] = set()

    for skill in job_skills_all:
        # Search nearby context in JD
        found = False
        for m in re.finditer(re.escape(skill), job_description, re.I):
            context = job_description[max(0, m.start() - 100): m.end() + 100]
            if preferred_signals.search(context):
                job_preferred_skills.add(skill)
                found = True
                break
            if required_signals.search(context):
                job_required_skills.add(skill)
                found = True
                break
        if not found:
            job_required_skills.add(skill)  # Default: treat as required

    matched_skills = list(resume_skills & job_skills_all)
    missing_required = list(job_required_skills - resume_skills)
    missing_preferred = list(job_preferred_skills - resume_skills)
    additional_skills = list(resume_skills - job_skills_all)

    if job_skills_all:
        skill_coverage = len(matched_skills) / len(job_skills_all) * 100
        # Weight required skills more heavily
        req_coverage = (
            len(resume_skills & job_required_skills) / len(job_required_skills) * 100
            if job_required_skills else skill_coverage
        )
        skill_score = round(0.7 * req_coverage + 0.3 * skill_coverage, 2)
    else:
        skill_score = 50.0  # No skills identified in JD
        limitations.append(
            "No skills were identified in the job description. "
            "Skill matching score defaulted to 50."
        )

    skill_score = min(100.0, skill_score)
    required_skill_coverage = round(
        len(resume_skills & job_required_skills) / max(len(job_required_skills), 1) * 100, 2
    )
    component_scores["skill"] = skill_score

    # ------------------------------------------------------------------
    # 3. Qualification matching
    # ------------------------------------------------------------------
    resume_quals = _extract_qualifications(resume_text)
    job_quals = _extract_qualifications(job_description)
    qual_score, qual_notes = _qualify_score(resume_quals, job_quals)
    component_scores["qualification"] = qual_score

    # ------------------------------------------------------------------
    # 4. Experience relevance
    # ------------------------------------------------------------------
    exp_score, exp_notes = _experience_score(resume_text, job_description)
    component_scores["experience"] = exp_score

    resume_exp_mentions = _extract_experience_mentions(resume_text)
    job_exp_mentions = _extract_experience_mentions(job_description)

    # ------------------------------------------------------------------
    # 5. Weighted final score (with proportional re-weighting for missing)
    # ------------------------------------------------------------------
    available_weights = {k: v for k, v in weights.items() if component_scores.get(k) is not None}
    total_weight = sum(available_weights.values())

    if total_weight == 0:
        overall = 0.0
    else:
        overall = sum(
            (w / total_weight) * component_scores[k]
            for k, w in available_weights.items()
        )

    overall = round(min(100.0, max(0.0, overall)), 2)

    # ------------------------------------------------------------------
    # 6. Keywords
    # ------------------------------------------------------------------
    jd_keywords = _extract_keywords(job_description, top_n=25)
    resume_keywords_set = set(_extract_keywords(resume_text, top_n=50))
    missing_kw = [kw for kw in jd_keywords if kw not in resume_keywords_set]

    # ------------------------------------------------------------------
    # 7. Improvement suggestions
    # ------------------------------------------------------------------
    suggestions: List[str] = []

    for skill in sorted(missing_required)[:5]:
        if skill in resume_skills:
            suggestions.append(
                f"You have '{skill}' — make it more prominent in your resume for this role."
            )
        else:
            suggestions.append(
                f"Consider developing '{skill}' skills, which is listed as a requirement."
            )

    for skill in sorted(missing_preferred)[:3]:
        suggestions.append(
            f"'{skill}' is listed as preferred — adding it would strengthen your application."
        )

    if not resume_quals and job_quals:
        suggestions.append(
            "Make your educational qualifications clearly visible in your resume "
            "(e.g., degree name, institution, graduation year)."
        )

    if missing_kw[:5]:
        suggestions.append(
            f"Consider incorporating relevant keywords from the job description into your resume: "
            f"{', '.join(missing_kw[:5])}."
        )

    if not suggestions:
        suggestions.append(
            "Your resume appears to be a strong match. "
            "Tailor specific project descriptions to mirror the job description language."
        )

    # ------------------------------------------------------------------
    # 8. Assemble limitations
    # ------------------------------------------------------------------
    limitations.append(
        "This score is an AI-estimated measure of resume-to-job-description text "
        "compatibility. It is NOT a hiring probability and does not reflect human "
        "judgment, company culture, or factors not present in the documents."
    )
    limitations.append(
        "Skill extraction uses keyword patterns and may miss contextual or implied skills."
    )
    if not resume_quals:
        limitations.append(
            "Qualification detection relies on standard degree abbreviations and may "
            "not detect all educational backgrounds."
        )

    return ScoreResult(
        overall_score=overall,
        match_category=score_to_category(overall),
        semantic_similarity_score=round(component_scores.get("semantic", 0), 2),
        skill_matching_score=round(component_scores.get("skill", 0), 2),
        qualification_matching_score=round(component_scores.get("qualification", 0), 2),
        experience_relevance_score=round(component_scores.get("experience", 0), 2),
        matched_skills=sorted(matched_skills),
        missing_required_skills=sorted(missing_required),
        missing_preferred_skills=sorted(missing_preferred),
        additional_skills=sorted(additional_skills),
        required_skill_coverage=required_skill_coverage,
        resume_qualifications=resume_quals,
        job_qualifications=job_quals,
        qualification_notes=qual_notes,
        resume_experience=resume_exp_mentions,
        job_experience_requirements=job_exp_mentions,
        experience_notes=exp_notes,
        important_keywords=jd_keywords[:20],
        missing_keywords=missing_kw[:15],
        improvement_suggestions=suggestions,
        limitations=limitations,
    )

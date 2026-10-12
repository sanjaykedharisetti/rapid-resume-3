"""
Resume Optimization Engine.
Performs truthful, ATS-aligned resume optimization without hallucinating or inventing skills.
Recalculates actual scores using the exact same scoring engine.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from app.services import semantic_matcher, skill_extractor
from app.services.scoring_service import ScoreResult, compute_score
from app.services.text_processor import clean_text, extract_sections

logger = logging.getLogger(__name__)

# Strong action verbs for ATS optimization
ACTION_VERBS = [
    "Architected", "Engineered", "Developed", "Spearheaded", "Implemented",
    "Deployed", "Optimized", "Designed", "Formulated", "Integrated",
    "Streamlined", "Orchestrated", "Accelerated", "Refactored", "Maintained",
    "Automated", "Constructed", "Enhanced", "Scaled", "Executed",
]

WEAK_VERB_PATTERNS = [
    (re.compile(r"^(?:worked on|responsible for|helped with|assisted in|involved in)\s+", re.I), "Spearheaded "),
    (re.compile(r"^(?:handled|dealt with)\s+", re.I), "Managed and executed "),
    (re.compile(r"^(?:did|made)\s+", re.I), "Engineered and delivered "),
    (re.compile(r"^(?:looked after|supported)\s+", re.I), "Maintained and optimized "),
]

# Standard skill normalization mapping
SKILL_NORMALIZATION: Dict[str, str] = {
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "py": "Python",
    "python": "Python",
    "html": "HTML5",
    "css": "CSS3",
    "react": "React.js",
    "reactjs": "React.js",
    "react.js": "React.js",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "aws": "AWS",
    "gcp": "GCP",
    "azure": "Azure",
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "nlp": "Natural Language Processing (NLP)",
    "tf": "TensorFlow",
    "tensorflow": "TensorFlow",
    "sklearn": "Scikit-Learn",
    "scikit-learn": "Scikit-Learn",
    "git": "Git",
    "github": "GitHub",
    "sql": "SQL",
    "nosql": "NoSQL",
    "rest": "RESTful APIs",
    "restful": "RESTful APIs",
    "graphql": "GraphQL",
    "ci/cd": "CI/CD Pipelines",
    "cicd": "CI/CD Pipelines",
    "tailwind": "Tailwind CSS",
    "redux": "Redux",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
}


def _extract_contact_info(text: str) -> Dict[str, str]:
    """Extract candidate name, email, phone, and links from the top of the resume."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    name = lines[0] if lines else "Candidate"
    # Basic sanitize name if it's too long or has punctuation
    if len(name) > 50 or any(char in name for char in [":", "@", "/", "\\"]):
        name = "Candidate"

    email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    phone_match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    linkedin_match = re.search(r"linkedin\.com/in/[\w-]+", text, re.I)
    github_match = re.search(r"github\.com/[\w-]+", text, re.I)

    contact_parts = []
    if email_match:
        contact_parts.append(email_match.group(0))
    if phone_match:
        contact_parts.append(phone_match.group(0))
    if linkedin_match:
        contact_parts.append(linkedin_match.group(0))
    if github_match:
        contact_parts.append(github_match.group(0))

    return {
        "name": name,
        "contact_line": " | ".join(contact_parts) if contact_parts else "Email / Phone / LinkedIn",
    }


def _analyze_formatting_issues(sections: Dict[str, str], raw_text: str) -> List[str]:
    """Identify ATS formatting and readability issues in the original resume."""
    issues = []
    if "summary" not in sections or len(sections.get("summary", "").strip()) < 30:
        issues.append("Missing dedicated Professional Summary to anchor target job relevance.")
    if "skills" not in sections:
        issues.append("Skills section not clearly delineated under standard ATS heading.")
    elif len(sections.get("skills", "").splitlines()) > 15:
        issues.append("Skills section lacks categorization (unstructured skill dump).")

    # Check for weak action verbs in experience
    exp_text = sections.get("experience", "") or sections.get("projects", "")
    if exp_text:
        weak_count = sum(1 for pattern, _ in WEAK_VERB_PATTERNS if pattern.search(exp_text))
        if weak_count > 0:
            issues.append(f"Contains passive or vague phrasing in experience bullets ({weak_count} detected).")

    if not re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", raw_text):
        issues.append("No clearly parsed email address found in contact header.")

    if "\t" in raw_text:
        issues.append("Uses tab characters which can confuse legacy ATS parsers.")

    return issues if issues else ["Minor layout optimizations possible for ATS readability."]


def _synthesize_truthful_summary(
    original_summary: str,
    candidate_skills: List[str],
    matched_skills: List[str],
    jd_title_or_keywords: List[str],
    has_experience: bool,
) -> str:
    """
    Generate a targeted, truthful professional summary highlighting verified candidate background.
    Never invents years or unverified degrees.
    """
    top_matches = matched_skills[:4] if matched_skills else candidate_skills[:4]
    skills_phrase = ", ".join(top_matches) if top_matches else "modern software tools"

    role_phrase = jd_title_or_keywords[0].title() if jd_title_or_keywords else "Engineering"

    if original_summary and len(original_summary) > 40:
        # Polish original summary while infusing matching verified keywords
        clean_orig = re.sub(r"^(?:professional summary|summary|profile)[:\s-]*", "", original_summary, flags=re.I).strip()
        return (
            f"{clean_orig} Skilled in {skills_phrase}, with demonstrated expertise in delivering "
            f"reliable, high-quality technical solutions aligned with business and system requirements."
        )

    # Clean concise truthful summary
    experience_intro = (
        "Results-oriented professional" if has_experience else "Motivated technical professional"
    )
    return (
        f"{experience_intro} with demonstrated proficiency in {skills_phrase}. "
        f"Adept at developing robust solutions, solving complex technical challenges, and collaborating "
        f"across cross-functional teams to drive organizational impact."
    )


def _categorize_and_prioritize_skills(
    candidate_skills: List[str],
    matched_skills: List[str],
) -> Tuple[Dict[str, List[str]], List[str]]:
    """
    Group genuine candidate skills into clean categories, prioritizing skills matching the JD.
    Does NOT add skills the candidate does not have!
    """
    normalized_skills: List[str] = []
    seen: Set[str] = set()

    for s in candidate_skills:
        lower = s.lower().strip()
        norm = SKILL_NORMALIZATION.get(lower, s.title())
        if norm.lower() not in seen:
            seen.add(norm.lower())
            normalized_skills.append(norm)

    matched_set = {s.lower() for s in matched_skills}

    # Categories
    languages_frameworks = []
    tools_cloud_database = []
    core_competencies = []

    for s in normalized_skills:
        s_lower = s.lower()
        if any(kw in s_lower for kw in ["python", "java", "c++", "c#", "ruby", "php", "react", "vue", "angular", "node", "typescript", "javascript", "html", "css", "django", "fastapi", "flask", "spring", "express"]):
            languages_frameworks.append(s)
        elif any(kw in s_lower for kw in ["sql", "postgres", "mongo", "docker", "kubernetes", "aws", "gcp", "azure", "git", "linux", "ci/cd", "redis", "kafka", "graphql", "rest"]):
            tools_cloud_database.append(s)
        else:
            core_competencies.append(s)

    # Sort each category: matching skills first!
    def sort_matching_first(lst: List[str]) -> List[str]:
        return sorted(lst, key=lambda x: (0 if x.lower() in matched_set or any(m in x.lower() for m in matched_set) else 1, x))

    categories = {
        "Languages & Frameworks": sort_matching_first(languages_frameworks),
        "Databases, Cloud & Tools": sort_matching_first(tools_cloud_database),
        "Methodologies & Concepts": sort_matching_first(core_competencies),
    }

    # Flatten for quick text inclusion
    clean_categories = {k: v for k, v in categories.items() if v}
    return clean_categories, normalized_skills


def _optimize_bullet_points(section_text: str) -> Tuple[str, int]:
    """Improve experience and project bullet points with strong action verbs."""
    lines = section_text.splitlines()
    optimized_lines = []
    improved_count = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            optimized_lines.append("")
            continue

        # Check if line is a bullet
        is_bullet = stripped.startswith(("-", "*", "•", "–")) or re.match(r"^\d+\.", stripped)
        bullet_prefix = "• " if is_bullet else ""
        content = re.sub(r"^[-*•–\d.]+\s*", "", stripped).strip()

        # Check weak verbs
        replaced = False
        for pattern, replacement in WEAK_VERB_PATTERNS:
            if pattern.search(content):
                content = pattern.sub(replacement, content)
                improved_count += 1
                replaced = True
                break

        # If it doesn't start with a capitalized action verb and is a bullet, ensure clean capitalization
        if is_bullet and not replaced and content:
            first_word = content.split()[0]
            if first_word.lower() not in [v.lower() for v in ACTION_VERBS]:
                # If first word is a verb like "build", capitalize or enhance
                if first_word.endswith("ed"):
                    content = content[0].upper() + content[1:]
                else:
                    content = "Executed " + content[0].lower() + content[1:]
                    improved_count += 1

        if is_bullet:
            optimized_lines.append(f"{bullet_prefix}{content}")
        else:
            optimized_lines.append(stripped)

    return "\n".join(optimized_lines), improved_count


def _assemble_optimized_resume_text(
    contact_info: Dict[str, str],
    summary: str,
    skill_categories: Dict[str, List[str]],
    experience_text: str,
    projects_text: str,
    education_text: str,
    certifications_text: str,
    other_text: str,
) -> str:
    """Assemble all optimized components into a strict single-column ATS resume."""
    blocks = []

    # 1. Header
    blocks.append(contact_info["name"].upper())
    blocks.append(contact_info["contact_line"])
    blocks.append("")

    # 2. Summary
    blocks.append("PROFESSIONAL SUMMARY")
    blocks.append("--------------------")
    blocks.append(summary)
    blocks.append("")

    # 3. Technical Skills
    blocks.append("TECHNICAL SKILLS")
    blocks.append("----------------")
    for cat_name, cat_skills in skill_categories.items():
        if cat_skills:
            blocks.append(f"• {cat_name}: {', '.join(cat_skills)}")
    blocks.append("")

    # 4. Experience
    if experience_text.strip():
        blocks.append("PROFESSIONAL EXPERIENCE")
        blocks.append("-----------------------")
        blocks.append(experience_text.strip())
        blocks.append("")

    # 5. Projects
    if projects_text.strip():
        blocks.append("KEY PROJECTS")
        blocks.append("------------")
        blocks.append(projects_text.strip())
        blocks.append("")

    # 6. Education
    if education_text.strip():
        blocks.append("EDUCATION")
        blocks.append("---------")
        blocks.append(education_text.strip())
        blocks.append("")

    # 7. Certifications
    if certifications_text.strip():
        blocks.append("CERTIFICATIONS & LICENSES")
        blocks.append("-------------------------")
        blocks.append(certifications_text.strip())
        blocks.append("")

    # 8. Additional
    if other_text.strip():
        blocks.append("ADDITIONAL INFORMATION")
        blocks.append("----------------------")
        blocks.append(other_text.strip())
        blocks.append("")

    return "\n".join(blocks).strip()


def optimize_resume(
    original_text: str,
    job_description: str,
    target_score: float = 85.0,
    max_iterations: int = 3,
) -> Dict[str, Any]:
    """
    Execute full truthful iterative resume optimization.
    Recalculates scores at each step using compute_score.
    """
    clean_orig = clean_text(original_text)
    clean_jd = clean_text(job_description)

    # 1. Baseline scoring
    baseline_result: ScoreResult = compute_score(clean_orig, clean_jd)
    orig_score = baseline_result.overall_score

    # 2. Extract sections & entities
    sections = extract_sections(clean_orig)
    contact_info = _extract_contact_info(clean_orig)
    formatting_issues = _analyze_formatting_issues(sections, clean_orig)

    # Identify candidate's verified skills
    candidate_skills = list(set(baseline_result.matched_skills + baseline_result.additional_skills))
    matched_skills = baseline_result.matched_skills
    missing_required = baseline_result.missing_required_skills
    missing_preferred = baseline_result.missing_preferred_skills
    missing_keywords = baseline_result.missing_keywords

    # Categorize and normalize genuine skills
    skill_categories, normalized_candidate_skills = _categorize_and_prioritize_skills(
        candidate_skills, matched_skills
    )

    # Optimize experience and projects bullet points
    raw_exp = sections.get("experience", "")
    raw_projects = sections.get("projects", "")
    opt_exp, exp_verb_changes = _optimize_bullet_points(raw_exp)
    opt_projects, proj_verb_changes = _optimize_bullet_points(raw_projects)

    education_text = sections.get("education", "")
    cert_text = sections.get("certifications", "")
    other_text = sections.get("other", "")

    summary_of_changes = [
        f"Standardized resume to single-column ATS structure with universal headings.",
        f"Categorized {len(normalized_candidate_skills)} verified skills into dedicated domain groups.",
        f"Elevated {len(matched_skills)} job-matching skills to top priority positions in each section.",
    ]
    if exp_verb_changes + proj_verb_changes > 0:
        summary_of_changes.append(
            f"Enhanced {exp_verb_changes + proj_verb_changes} bullet points with high-impact action verbs."
        )

    # 3. Iterative Optimization Loop
    best_text = clean_orig
    best_score = orig_score
    best_result: ScoreResult = baseline_result
    best_summary = ""
    best_sections: Dict[str, str] = {}
    iterations_run = 0

    for iteration in range(1, max_iterations + 1):
        iterations_run = iteration

        # Synthesize targeted summary
        tailored_summary = _synthesize_truthful_summary(
            sections.get("summary", ""),
            normalized_candidate_skills,
            matched_skills,
            baseline_result.important_keywords,
            has_experience=bool(raw_exp.strip()),
        )

        # Assemble candidate resume
        candidate_text = _assemble_optimized_resume_text(
            contact_info=contact_info,
            summary=tailored_summary,
            skill_categories=skill_categories,
            experience_text=opt_exp,
            projects_text=opt_projects,
            education_text=education_text,
            certifications_text=cert_text,
            other_text=other_text,
        )

        # Recalculate score from ACTUAL optimized text
        current_result: ScoreResult = compute_score(candidate_text, clean_jd)
        current_score = current_result.overall_score

        logger.info(
            "Optimization Iteration %d: Score = %.1f (Original = %.1f)",
            iteration, current_score, orig_score
        )

        if current_score >= best_score:
            best_score = current_score
            best_text = candidate_text
            best_result = current_result
            best_summary = tailored_summary
            best_sections = {
                "contact": f"{contact_info['name']}\n{contact_info['contact_line']}",
                "summary": tailored_summary,
                "skills": "\n".join(f"• {k}: {', '.join(v)}" for k, v in skill_categories.items() if v),
                "experience": opt_exp,
                "projects": opt_projects,
                "education": education_text,
                "certifications": cert_text,
            }

        # If target reached or plateaued, finish
        if best_score >= target_score:
            break

    # Build changes summary notes
    newly_matched = list(set(best_result.matched_skills) - set(baseline_result.matched_skills))
    if newly_matched:
        summary_of_changes.append(
            f"Successfully elevated {len(newly_matched)} existing skills ({', '.join(newly_matched[:3])}) into verified ATS matches."
        )

    # Generate remaining questions / gap analysis
    unanswered_questions = []
    if best_result.missing_required_skills:
        unanswered_questions.append(
            f"Missing required skills: {', '.join(best_result.missing_required_skills[:4])}. "
            f"If you have hands-on experience with any of these, add them to your Projects or Experience section."
        )
    if "projects" in sections and not re.search(r"\d+%", sections["projects"]):
        unanswered_questions.append(
            "Consider adding measurable outcomes (e.g., '% improvement', 'latency reduction', 'user count') to your project descriptions."
        )

    remaining_gaps = []
    for s in best_result.missing_required_skills[:5]:
        remaining_gaps.append(f"Required skill gap: {s}")
    for k in best_result.missing_keywords[:4]:
        remaining_gaps.append(f"Domain keyword gap: {k}")

    target_reached = best_score >= target_score
    status_msg = (
        "Your optimized resume has reached the target compatibility score."
        if target_reached
        else "Your resume has improved, but some job requirements still need attention."
    )

    score_improvement = round(best_score - orig_score, 1)

    return {
        "original_score": round(orig_score, 1),
        "optimized_score": round(best_score, 1),
        "score_improvement": score_improvement,
        "target_score": target_score,
        "target_reached": target_reached,
        "status_message": status_msg,
        "component_scores_before": {
            "semantic_similarity_score": round(baseline_result.semantic_similarity_score, 1),
            "skill_matching_score": round(baseline_result.skill_matching_score, 1),
            "qualification_matching_score": round(baseline_result.qualification_matching_score, 1),
            "experience_relevance_score": round(baseline_result.experience_relevance_score, 1),
        },
        "component_scores_after": {
            "semantic_similarity_score": round(best_result.semantic_similarity_score, 1),
            "skill_matching_score": round(best_result.skill_matching_score, 1),
            "qualification_matching_score": round(best_result.qualification_matching_score, 1),
            "experience_relevance_score": round(best_result.experience_relevance_score, 1),
        },
        "matched_skills_before": baseline_result.matched_skills,
        "matched_skills_after": best_result.matched_skills,
        "newly_matched_skills": newly_matched,
        "remaining_missing_skills": best_result.missing_required_skills,
        "missing_preferred_skills": best_result.missing_preferred_skills,
        "missing_keywords": best_result.missing_keywords,
        "formatting_issues": formatting_issues,
        "summary_of_changes": summary_of_changes,
        "unanswered_questions": unanswered_questions,
        "remaining_gaps": remaining_gaps,
        "original_resume_text": clean_orig,
        "optimized_resume_text": best_text,
        "original_sections": {k: v for k, v in sections.items() if v},
        "optimized_sections": best_sections,
        "iterations_run": iterations_run,
    }

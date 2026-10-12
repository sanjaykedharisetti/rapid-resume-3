"""
Skill extraction service.

Uses a configurable skill dictionary with carefully designed regex patterns
to avoid naive substring matching (e.g. "Java" must not match inside
"JavaScript").

New skills can be added to SKILL_DICTIONARY without any other code changes.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class SkillEntry:
    """A single skill with its canonical name and match patterns."""

    canonical: str
    # Aliases are lower-cased strings; we build word-boundary patterns from them
    aliases: List[str] = field(default_factory=list)
    # Category for grouping in UI
    category: str = "general"
    # If True, requires word boundaries; if False, uses custom pattern
    word_boundary: bool = True
    # Optional custom regex pattern (overrides word_boundary logic)
    custom_pattern: Optional[str] = None


# ---------------------------------------------------------------------------
# Skill dictionary
# ---------------------------------------------------------------------------
# Add new skills here.  Rules:
#   - Keep aliases lower-cased.
#   - If a skill contains regex meta-characters, escape them or use custom_pattern.
#   - For skills like "C++" use custom_pattern to avoid regex issues.
# ---------------------------------------------------------------------------

SKILL_DICTIONARY: List[SkillEntry] = [
    # --- Programming Languages ---
    SkillEntry("Python", ["python"], category="programming"),
    # Java must NOT match "JavaScript" – use negative lookahead
    SkillEntry(
        "Java",
        aliases=["java"],
        category="programming",
        custom_pattern=r"\bjava(?!script)\b",
    ),
    SkillEntry(
        "JavaScript",
        aliases=["javascript", "js"],
        category="programming",
        custom_pattern=r"\bjavascript\b|\bjs\b",
    ),
    SkillEntry(
        "TypeScript",
        aliases=["typescript", "ts"],
        category="programming",
        custom_pattern=r"\btypescript\b|\bts\b",
    ),
    SkillEntry(
        "C++",
        aliases=["c++", "cpp"],
        category="programming",
        custom_pattern=r"\bc\+\+\b|\bcpp\b",
    ),
    SkillEntry(
        "C#",
        aliases=["c#", "csharp", "c sharp"],
        category="programming",
        custom_pattern=r"\bc#\b|\bcsharp\b|\bc\s+sharp\b",
    ),
    SkillEntry("C", aliases=["c language", " c "], category="programming", custom_pattern=r"\bC\b(?!\+\+|#|\s*sharp)"),
    SkillEntry("Go", aliases=["golang", "go language"], category="programming", custom_pattern=r"\bgolang\b|\bgo\b(?!\s*\.)"),
    SkillEntry("Rust", aliases=["rust"], category="programming"),
    SkillEntry("Kotlin", aliases=["kotlin"], category="programming"),
    SkillEntry("Swift", aliases=["swift"], category="programming"),
    SkillEntry("R", aliases=["r language", "r programming"], category="programming", custom_pattern=r"\bR\b(?!\s*eact)"),
    SkillEntry("Scala", aliases=["scala"], category="programming"),
    SkillEntry("Ruby", aliases=["ruby"], category="programming"),
    SkillEntry("PHP", aliases=["php"], category="programming"),
    SkillEntry("Perl", aliases=["perl"], category="programming"),
    SkillEntry("MATLAB", aliases=["matlab"], category="programming"),
    SkillEntry("Shell/Bash", aliases=["bash", "shell script", "shell scripting", "bash scripting"], category="programming"),

    # --- Web Frameworks ---
    SkillEntry("React", aliases=["react", "reactjs", "react.js"], category="web"),
    SkillEntry("Vue.js", aliases=["vue", "vuejs", "vue.js"], category="web"),
    SkillEntry("Angular", aliases=["angular", "angularjs"], category="web"),
    SkillEntry("Next.js", aliases=["next.js", "nextjs"], category="web"),
    SkillEntry("Node.js", aliases=["node.js", "nodejs", "node"], category="web"),
    SkillEntry("Express.js", aliases=["express", "expressjs", "express.js"], category="web"),
    SkillEntry("Django", aliases=["django"], category="web"),
    SkillEntry("Flask", aliases=["flask"], category="web"),
    SkillEntry("FastAPI", aliases=["fastapi"], category="web"),
    SkillEntry("Spring Boot", aliases=["spring boot", "spring"], category="web"),
    SkillEntry("Laravel", aliases=["laravel"], category="web"),
    SkillEntry("ASP.NET", aliases=["asp.net", "asp net"], category="web"),
    SkillEntry("GraphQL", aliases=["graphql"], category="web"),
    SkillEntry("REST API", aliases=["rest api", "restful", "rest"], category="web"),

    # --- Databases ---
    SkillEntry("SQL", aliases=["sql"], category="database"),
    SkillEntry("MySQL", aliases=["mysql"], category="database"),
    SkillEntry("PostgreSQL", aliases=["postgresql", "postgres"], category="database"),
    SkillEntry("SQLite", aliases=["sqlite"], category="database"),
    SkillEntry("MongoDB", aliases=["mongodb", "mongo"], category="database"),
    SkillEntry("Redis", aliases=["redis"], category="database"),
    SkillEntry("Elasticsearch", aliases=["elasticsearch", "elastic search"], category="database"),
    SkillEntry("Cassandra", aliases=["cassandra"], category="database"),
    SkillEntry("Oracle", aliases=["oracle db", "oracle database"], category="database"),
    SkillEntry("SQL Server", aliases=["sql server", "mssql", "microsoft sql server"], category="database"),
    SkillEntry("DynamoDB", aliases=["dynamodb"], category="database"),
    SkillEntry("Firebase", aliases=["firebase"], category="database"),

    # --- Cloud & DevOps ---
    SkillEntry("AWS", aliases=["aws", "amazon web services"], category="cloud"),
    SkillEntry("Google Cloud", aliases=["google cloud", "gcp", "google cloud platform"], category="cloud"),
    SkillEntry("Azure", aliases=["azure", "microsoft azure"], category="cloud"),
    SkillEntry("Docker", aliases=["docker"], category="devops"),
    SkillEntry("Kubernetes", aliases=["kubernetes", "k8s"], category="devops"),
    SkillEntry("Terraform", aliases=["terraform"], category="devops"),
    SkillEntry("Ansible", aliases=["ansible"], category="devops"),
    SkillEntry("Jenkins", aliases=["jenkins"], category="devops"),
    SkillEntry("GitHub Actions", aliases=["github actions"], category="devops"),
    SkillEntry("CI/CD", aliases=["ci/cd", "ci cd", "continuous integration", "continuous deployment"], category="devops"),
    SkillEntry("Git", aliases=["git"], category="devops"),
    SkillEntry("Linux", aliases=["linux", "unix"], category="devops"),

    # --- ML / AI ---
    SkillEntry("Machine Learning", aliases=["machine learning", "ml"], category="ml"),
    SkillEntry("Deep Learning", aliases=["deep learning", "dl"], category="ml"),
    SkillEntry("Natural Language Processing", aliases=["nlp", "natural language processing"], category="ml"),
    SkillEntry("Computer Vision", aliases=["computer vision", "cv"], category="ml"),
    SkillEntry("TensorFlow", aliases=["tensorflow"], category="ml"),
    SkillEntry("PyTorch", aliases=["pytorch"], category="ml"),
    SkillEntry("Keras", aliases=["keras"], category="ml"),
    SkillEntry("Scikit-learn", aliases=["scikit-learn", "sklearn"], category="ml"),
    SkillEntry("Pandas", aliases=["pandas"], category="ml"),
    SkillEntry("NumPy", aliases=["numpy"], category="ml"),
    SkillEntry("Data Analysis", aliases=["data analysis", "data analytics"], category="ml"),
    SkillEntry("Data Science", aliases=["data science"], category="ml"),
    SkillEntry("Statistics", aliases=["statistics", "statistical analysis"], category="ml"),
    SkillEntry("Tableau", aliases=["tableau"], category="analytics"),
    SkillEntry("Power BI", aliases=["power bi", "powerbi"], category="analytics"),

    # --- Soft Skills ---
    SkillEntry("Communication", aliases=["communication", "written communication", "verbal communication"], category="soft"),
    SkillEntry("Leadership", aliases=["leadership", "team leadership"], category="soft"),
    SkillEntry("Problem Solving", aliases=["problem solving", "problem-solving"], category="soft"),
    SkillEntry("Teamwork", aliases=["teamwork", "collaboration", "team player"], category="soft"),
    SkillEntry("Agile", aliases=["agile", "scrum", "kanban"], category="soft"),
    SkillEntry("Project Management", aliases=["project management"], category="soft"),

    # --- Other Technical ---
    SkillEntry("HTML", aliases=["html", "html5"], category="web"),
    SkillEntry("CSS", aliases=["css", "css3", "scss", "sass"], category="web"),
    SkillEntry("Microservices", aliases=["microservices", "microservice"], category="architecture"),
    SkillEntry("System Design", aliases=["system design"], category="architecture"),
    SkillEntry("API Design", aliases=["api design"], category="architecture"),
    SkillEntry("Cybersecurity", aliases=["cybersecurity", "security", "information security"], category="security"),
]


# ---------------------------------------------------------------------------
# Compiled patterns cache
# ---------------------------------------------------------------------------

@dataclass
class _CompiledSkill:
    canonical: str
    category: str
    pattern: re.Pattern


def _compile_skills() -> List[_CompiledSkill]:
    compiled: List[_CompiledSkill] = []
    for entry in SKILL_DICTIONARY:
        if entry.custom_pattern:
            pat = re.compile(entry.custom_pattern, re.IGNORECASE)
        else:
            # Build word-boundary pattern from aliases
            alias_patterns = [r"\b" + re.escape(a) + r"\b" for a in entry.aliases]
            pat = re.compile("|".join(alias_patterns), re.IGNORECASE)
        compiled.append(_CompiledSkill(entry.canonical, entry.category, pat))
    return compiled


_COMPILED_SKILLS: List[_CompiledSkill] = _compile_skills()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_skills(text: str) -> List[str]:
    """
    Extract a de-duplicated, sorted list of canonical skill names from text.
    """
    found: Set[str] = set()
    for skill in _COMPILED_SKILLS:
        if skill.pattern.search(text):
            found.add(skill.canonical)
    return sorted(found)


def extract_skills_with_categories(text: str) -> Dict[str, List[str]]:
    """
    Return skills grouped by category.
    """
    result: Dict[str, List[str]] = {}
    for skill in _COMPILED_SKILLS:
        if skill.pattern.search(text):
            result.setdefault(skill.category, []).append(skill.canonical)
    return result


def get_all_canonical_skills() -> List[str]:
    """Return all canonical skill names in the dictionary."""
    return [e.canonical for e in SKILL_DICTIONARY]

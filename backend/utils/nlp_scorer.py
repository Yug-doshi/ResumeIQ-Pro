"""
NLP Scorer — TF-IDF + spaCy based resume scoring

Works alongside the LSTM scorer as a complementary analysis engine.
Handles:
  - ATS score calculation via TF-IDF cosine similarity
  - Skill extraction from text
  - Missing skill detection
  - Format quality scoring
"""

import re
import numpy as np
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── Try loading spaCy (optional — works without it) ──
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except Exception:
    SPACY_AVAILABLE = False
    print("[INFO] spaCy model not found. Using basic NLP. Run: python -m spacy download en_core_web_sm")

# ── Try loading NLTK (optional) ──
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab', quiet=True)
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


# =====================================================================
#  TECH SKILLS DATABASE (comprehensive)
# =====================================================================

TECH_SKILLS = {
    # Programming Languages
    "python": ["python", "py"],
    "javascript": ["javascript", "js", "node.js", "nodejs"],
    "java": ["java"],
    "csharp": ["c#", "csharp", ".net", "dotnet"],
    "cpp": ["c++", "cpp"],
    "typescript": ["typescript", "ts"],
    "go": ["go", "golang"],
    "rust": ["rust"],
    "ruby": ["ruby"],
    "php": ["php"],
    "swift": ["swift"],
    "kotlin": ["kotlin"],
    "r": ["r programming", "r language"],
    "sql": ["sql", "mysql", "postgresql", "sqlite", "t-sql"],
    "html": ["html", "html5"],
    "css": ["css", "css3", "sass", "scss", "less"],

    # Frontend Frameworks
    "react": ["react", "reactjs", "react.js"],
    "angular": ["angular", "angularjs"],
    "vue": ["vue", "vuejs", "vue.js"],
    "next.js": ["next.js", "nextjs", "next"],
    "svelte": ["svelte"],
    "tailwind": ["tailwind", "tailwindcss"],
    "bootstrap": ["bootstrap"],

    # Backend Frameworks
    "fastapi": ["fastapi"],
    "django": ["django"],
    "flask": ["flask"],
    "express": ["express", "express.js"],
    "spring": ["spring", "spring boot", "springboot"],
    "laravel": ["laravel"],
    "rails": ["ruby on rails", "rails"],

    # Data Science & ML
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "tensorflow": ["tensorflow", "tf"],
    "pytorch": ["pytorch", "torch"],
    "keras": ["keras"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "neural network", "neural networks"],
    "nlp": ["nlp", "natural language processing"],
    "computer vision": ["computer vision", "cv", "opencv"],
    "data analysis": ["data analysis", "data analytics"],
    "data visualization": ["data visualization", "matplotlib", "seaborn", "plotly"],

    # Databases
    "mongodb": ["mongodb", "mongo"],
    "firebase": ["firebase"],
    "redis": ["redis"],
    "elasticsearch": ["elasticsearch"],
    "dynamodb": ["dynamodb"],
    "cassandra": ["cassandra"],

    # DevOps & Cloud
    "docker": ["docker", "containerization"],
    "kubernetes": ["kubernetes", "k8s"],
    "aws": ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "gcp": ["gcp", "google cloud"],
    "azure": ["azure", "microsoft azure"],
    "ci/cd": ["ci/cd", "cicd", "continuous integration", "continuous deployment"],
    "jenkins": ["jenkins"],
    "terraform": ["terraform"],
    "ansible": ["ansible"],

    # Tools & Practices
    "git": ["git", "github", "gitlab", "bitbucket"],
    "linux": ["linux", "ubuntu", "centos"],
    "api": ["api", "rest", "restful", "graphql"],
    "agile": ["agile", "scrum", "kanban"],
    "testing": ["testing", "unit test", "pytest", "jest", "selenium"],
    "microservices": ["microservices", "micro-services"],
}

# ── Role-specific required skills ──
ROLE_REQUIRED_SKILLS = {
    "software engineer": ["python", "javascript", "sql", "git", "api", "docker", "testing", "agile", "linux", "react", "css", "html", "typescript", "mongodb", "express"],
    "data scientist": ["python", "sql", "pandas", "numpy", "scikit-learn", "machine learning", "data visualization", "tensorflow", "pytorch", "data analysis", "git"],
    "ai engineer": ["python", "tensorflow", "pytorch", "deep learning", "machine learning", "nlp", "docker", "api", "computer vision", "git", "numpy", "pandas"],
    "web developer": ["html", "css", "javascript", "react", "api", "git", "sql", "tailwind", "typescript", "express", "mongodb", "next.js", "bootstrap"],
    "devops engineer": ["docker", "kubernetes", "aws", "linux", "ci/cd", "terraform", "git", "python", "jenkins", "agile"],
    "product manager": ["agile", "sql", "api", "data analysis", "git", "testing"],
    "backend developer": ["python", "sql", "api", "docker", "git", "linux", "testing", "mongodb", "express", "fastapi", "django", "redis"],
    "frontend developer": ["javascript", "react", "html", "css", "typescript", "git", "testing", "api", "next.js", "tailwind", "bootstrap", "vue"],
    "full stack developer": ["javascript", "react", "python", "sql", "api", "git", "docker", "html", "css", "mongodb", "express", "typescript", "next.js"],
    "ml engineer": ["python", "tensorflow", "pytorch", "docker", "machine learning", "api", "aws", "sql", "numpy", "pandas", "scikit-learn"],
}


# =====================================================================
#  MAIN SCORING FUNCTION
# =====================================================================

def calculate_ats_score(resume_text: str, job_description: str, job_role: str) -> Tuple[int, float]:
    """
    Calculate ATS score (0-100) using TF-IDF cosine similarity + keyword analysis
    + direct skill matching.

    Args:
        resume_text:     Full resume text
        job_description: Job description (can be empty)
        job_role:        Target job role name

    Returns:
        Tuple of (ats_score, keyword_match_percentage)
    """
    if not resume_text:
        return 25, 0.0

    resume_clean = _clean_text(resume_text)

    # ── If no JD, score based on role requirements ──
    if not job_description or not job_description.strip():
        return _score_without_jd(resume_clean, job_role)

    jd_clean = _clean_text(job_description)

    # ── Signal 1: TF-IDF similarity ──
    try:
        vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([resume_clean, jd_clean])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except Exception:
        similarity = 0.3
    # Scale up low similarities (TF-IDF between resume/JD is naturally low)
    similarity_score = min(100, similarity * 250)  # 0.2 → 50, 0.4 → 100

    # ── Signal 2: Keyword matching (filtered) ──
    job_keywords = _extract_keywords(jd_clean)
    resume_lower = resume_text.lower()
    matched_count = sum(1 for kw in job_keywords if kw.lower() in resume_lower)
    keyword_percentage = (matched_count / max(1, len(job_keywords))) * 100

    # ── Signal 3: Direct tech skill match ──
    resume_skills = extract_skills(resume_text)
    role_key = job_role.lower().strip()
    required = ROLE_REQUIRED_SKILLS.get(role_key, ROLE_REQUIRED_SKILLS.get("software engineer"))
    found_lower = set(s.lower() for s in resume_skills)
    skill_match_count = sum(1 for s in required if s in found_lower)
    skill_match_pct = (skill_match_count / max(1, len(required))) * 100

    # ── Signal 4: Skill breadth bonus ──
    # Reward having many relevant skills beyond the required list
    breadth_bonus = min(100, len(resume_skills) * 6)  # 17 skills → 100

    # ── Signal 5: Format quality ──
    format_score = _calculate_format_score(resume_text)

    # ── Combined score with better weights ──
    combined = (
        similarity_score * 0.15 +     # TF-IDF text similarity
        keyword_percentage * 0.20 +    # JD keyword matching
        skill_match_pct * 0.25 +       # Direct skill overlap
        breadth_bonus * 0.15 +         # Total skill breadth
        format_score * 0.25            # Resume quality & completeness
    )

    ats_score = min(100, max(0, int(combined)))
    return ats_score, round(keyword_percentage, 1)


def _score_without_jd(resume_clean: str, job_role: str) -> Tuple[int, float]:
    """Score resume without a job description, using role requirements."""
    role_key = job_role.lower().strip()
    required = ROLE_REQUIRED_SKILLS.get(role_key, ROLE_REQUIRED_SKILLS.get("software engineer"))

    # Check how many role skills are in the resume
    found = extract_skills(resume_clean)
    found_lower = set(s.lower() for s in found)
    matched = sum(1 for s in required if s in found_lower)
    keyword_pct = (matched / max(1, len(required))) * 100

    # Also reward total skill count (breadth of skills)
    total_skills_bonus = min(20, len(found) * 2)  # up to 20 pts for having many skills

    format_score = _calculate_format_score(resume_clean)
    ats = int(keyword_pct * 0.55 + format_score * 0.25 + total_skills_bonus)
    ats = min(100, max(0, ats))

    return ats, round(keyword_pct, 1)


# =====================================================================
#  SKILL EXTRACTION
# =====================================================================

def extract_skills(text: str) -> List[str]:
    """Extract technical skills found in text."""
    text_lower = text.lower()
    found_skills = set()

    for skill_name, keywords in TECH_SKILLS.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_skills.add(skill_name)
                break

    return sorted(list(found_skills))


def get_missing_skills(extracted_skills: List[str], required_skills: List[str]) -> List[str]:
    """Find skills required but not present in resume."""
    if not required_skills:
        return []

    extracted_lower = set(s.lower() for s in extracted_skills)
    missing = [s for s in required_skills if s.lower() not in extracted_lower]
    return missing


# =====================================================================
#  HELPER FUNCTIONS
# =====================================================================

def _clean_text(text: str) -> str:
    """Clean and normalize text for analysis."""
    text = re.sub(r'[^a-zA-Z0-9\s.#+]', ' ', text)
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _extract_keywords(text: str) -> List[str]:
    """Extract important keywords from text, with comprehensive filtering."""
    if SPACY_AVAILABLE:
        doc = nlp(text[:5000])
        keywords = [
            token.text for token in doc
            if not token.is_stop and not token.is_punct and len(token.text) > 2
        ]
        return list(set(keywords))

    # Fallback: comprehensive stop word filtering
    words = text.split()
    stop_words = {
        # Standard stop words
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'shall', 'would',
        'should', 'may', 'might', 'can', 'could', 'and', 'or', 'but', 'in',
        'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'into',
        'that', 'this', 'it', 'not', 'no', 'so', 'if', 'we', 'you', 'they',
        'our', 'your', 'their', 'its', 'all', 'each', 'every', 'any', 'some',
        # JD-specific common words that inflate keyword count
        'looking', 'seeking', 'join', 'team', 'role', 'position', 'work',
        'working', 'experience', 'years', 'strong', 'excellent', 'good',
        'required', 'requirements', 'preferred', 'including', 'ability',
        'must', 'need', 'needs', 'please', 'apply', 'company', 'job',
        'candidate', 'ideal', 'responsible', 'responsibilities', 'skills',
        'about', 'well', 'also', 'such', 'like', 'use', 'using', 'used',
        'related', 'relevant', 'field', 'based', 'new', 'help', 'make',
        'develop', 'developing', 'creating', 'create', 'building', 'build',
        'ensure', 'maintain', 'support', 'provide', 'understand', 'knowledge',
        'write', 'writing', 'written', 'read', 'reading', 'learn', 'learning',
        'plus', 'bonus', 'points', 'nice', 'equivalent', 'practical', 'hands',
        'verbal', 'oral', 'effectively', 'within', 'across', 'through',
        'including', 'includes', 'other', 'day', 'daily', 'high', 'highly',
        'level', 'time', 'quality', 'best', 'practices', 'end', 'full',
        'proficiency', 'proficient', 'familiarity', 'familiar',
    }
    keywords = [w for w in words if w.lower() not in stop_words and len(w) > 2]
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower not in seen:
            seen.add(kw_lower)
            unique.append(kw)
    return unique


def _calculate_format_score(text: str) -> float:
    """
    Score resume format quality (0-100).
    Considers sections present, content depth, skills density, contact info,
    and professional structure.
    """
    import re
    score = 0
    text_lower = text.lower()
    word_count = len(text.split())

    # ── Section presence (up to 35 pts) ──
    # Include common alternate headings so internships/achievements count too.
    sections = [
        "experience", "work experience", "professional experience", "employment",
        "internship", "intern", "training",
        "education",
        "skills", "technical skills", "technologies", "tools",
        "projects", "portfolio",
        "summary", "objective", "profile", "about",
        "certif", "certification", "certifications",
        "achievement", "achievements", "award", "awards", "honors",
        "publication", "publications",
        "leadership", "extracurricular", "volunteer",
    ]
    section_count = sum(1 for s in sections if s in text_lower)
    score += min(35, section_count * 7)

    # ── Content depth (up to 20 pts) ──
    if word_count >= 400:
        score += 20
    elif word_count >= 250:
        score += 15
    elif word_count >= 150:
        score += 10
    elif word_count >= 80:
        score += 5

    # ── Technical skill density (up to 20 pts) ──
    tech_keywords = [
        'python', 'java', 'javascript', 'react', 'sql', 'aws', 'docker',
        'tensorflow', 'machine learning', 'api', 'git', 'linux', 'node',
        'typescript', 'html', 'css', 'mongodb', 'kubernetes', 'flask', 'django',
        'express', 'redis', 'postgresql', 'angular', 'vue', 'pytorch',
    ]
    tech_found = sum(1 for kw in tech_keywords if kw in text_lower)
    if tech_found >= 10:
        score += 20
    elif tech_found >= 6:
        score += 15
    elif tech_found >= 3:
        score += 10
    elif tech_found >= 1:
        score += 5

    # ── Contact info (up to 10 pts) ──
    if re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text):
        score += 4
    if re.search(r'[\+]?[\d\s\-\(\)]{10,}', text):
        score += 3
    if any(w in text_lower for w in ['linkedin', 'github']):
        score += 3

    # ── Action verbs / impact language (up to 15 pts) ──
    action_verbs = ['developed', 'implemented', 'designed', 'led', 'managed',
                   'created', 'built', 'optimized', 'improved', 'deployed',
                   'delivered', 'architected', 'automated', 'integrated']
    verb_count = sum(1 for v in action_verbs if v in text_lower)
    score += min(15, verb_count * 3)

    return min(100, score)

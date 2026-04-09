"""
ATS Keyword Optimizer — Identifies high-value keywords to add to resume

Compares resume against job description and:
  1. Finds exact keyword matches
  2. Finds semantically similar terms
  3. Identifies high-impact missing keywords
  4. Suggests where to place keywords in the resume
  5. Provides keyword density analysis
"""

from typing import Dict, List, Tuple
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter


# ── Keyword categories with importance weights ──
KEYWORD_WEIGHTS = {
    "technical_must_have": 3.0,  # programming languages, frameworks
    "role_specific": 2.5,       # role-specific tools
    "methodology": 1.5,         # agile, scrum, etc.
    "soft_skill": 1.0,          # leadership, communication
    "certification": 2.0,       # AWS certified, etc.
    "education": 1.0,           # degree, university
}

# ── Common ATS-important keyword patterns ──
ACTION_VERB_PATTERNS = [
    "developed", "implemented", "designed", "led", "managed", "built",
    "created", "optimized", "improved", "reduced", "increased", "launched",
    "delivered", "architected", "automated", "deployed", "migrated",
    "integrated", "scaled", "mentored", "collaborated", "analyzed",
    "configured", "monitored", "tested", "refactored", "maintained",
]

METRIC_PATTERNS = [
    r'\d+%', r'\$\d+', r'\d+[KkMm]\+?', r'\d+\s*(users|clients|customers)',
    r'\d+\s*(team|engineers|developers)', r'\d+x\s*improvement',
]


def analyze_keywords(resume_text: str, job_description: str, job_role: str = "") -> Dict:
    """
    Deep keyword analysis between resume and job description.

    Returns:
    {
      "matched_keywords": [{"keyword": str, "count": int, "importance": str}],
      "missing_keywords": [{"keyword": str, "importance": str, "suggestion": str}],
      "keyword_density": {"resume": float, "optimal": float},
      "action_verbs": {"found": [str], "missing": [str], "score": int},
      "metrics_found": [str],
      "ats_optimization_score": int,
      "placement_suggestions": [str],
      "overall_recommendations": [str],
    }
    """
    if not job_description:
        return _basic_analysis(resume_text)

    resume_lower = resume_text.lower()
    jd_lower = job_description.lower()

    # ── Extract keywords from JD using TF-IDF ──
    jd_keywords = _extract_tfidf_keywords(job_description, top_n=40)

    # ── Categorize matches ──
    matched = []
    missing = []

    for keyword in jd_keywords:
        kw_lower = keyword.lower()
        count = resume_lower.count(kw_lower)

        importance = _classify_importance(keyword)

        if count > 0:
            matched.append({
                "keyword": keyword,
                "count": count,
                "importance": importance,
            })
        else:
            suggestion = _get_placement_suggestion(keyword, importance)
            missing.append({
                "keyword": keyword,
                "importance": importance,
                "suggestion": suggestion,
            })

    # Sort: high importance missing keywords first
    importance_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    missing.sort(key=lambda x: importance_order.get(x["importance"], 3))
    matched.sort(key=lambda x: importance_order.get(x["importance"], 3))

    # ── Action verb analysis ──
    found_verbs = [v for v in ACTION_VERB_PATTERNS if v in resume_lower]
    missing_verbs = [v for v in ACTION_VERB_PATTERNS if v not in resume_lower][:8]
    verb_score = min(100, int(len(found_verbs) / max(1, 8) * 100))

    # ── Metrics detection ──
    metrics_found = []
    for pattern in METRIC_PATTERNS:
        matches = re.findall(pattern, resume_text, re.IGNORECASE)
        metrics_found.extend(matches)
    metrics_found = list(set(metrics_found))[:10]

    # ── Keyword density ──
    resume_words = len(resume_lower.split())
    matched_word_count = sum(m["count"] for m in matched)
    density = (matched_word_count / max(1, resume_words)) * 100

    # ── ATS optimization score ──
    match_ratio = len(matched) / max(1, len(matched) + len(missing))
    ats_opt_score = int(
        match_ratio * 50 +                          # keyword match ratio (up to 50)
        min(20, verb_score * 0.2) +                  # action verbs (up to 20)
        min(20, len(metrics_found) * 4) +            # quantifiable metrics (up to 20)
        min(10, len(matched) * 1.5)                  # bonus for absolute matches (up to 10)
    )
    ats_opt_score = min(100, max(0, ats_opt_score))

    # ── Placement suggestions ──
    placements = _generate_placement_suggestions(missing[:5])

    # ── Overall recommendations ──
    recommendations = _generate_recommendations(
        matched, missing, found_verbs, missing_verbs, metrics_found, ats_opt_score
    )

    return {
        "matched_keywords": matched[:15],
        "missing_keywords": missing[:12],
        "keyword_density": {
            "current": round(density, 2),
            "optimal": 3.5,
            "status": "good" if 2.0 <= density <= 5.0 else "needs improvement"
        },
        "action_verbs": {
            "found": found_verbs[:10],
            "missing": missing_verbs[:6],
            "score": verb_score,
        },
        "metrics_found": metrics_found,
        "ats_optimization_score": ats_opt_score,
        "placement_suggestions": placements,
        "overall_recommendations": recommendations,
    }


def _extract_tfidf_keywords(text: str, top_n: int = 40) -> List[str]:
    """Extract top keywords using TF-IDF."""
    try:
        # Use word ngrams (1-2 words)
        vectorizer = TfidfVectorizer(
            max_features=200,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
        )
        tfidf_matrix = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]

        # Sort by TF-IDF score
        keyword_scores = list(zip(feature_names, scores))
        keyword_scores.sort(key=lambda x: x[1], reverse=True)

        # Filter out very short or very common words
        keywords = []
        for kw, score in keyword_scores:
            if len(kw) > 2 and score > 0.01:
                keywords.append(kw)
            if len(keywords) >= top_n:
                break

        return keywords
    except Exception:
        # Fallback: simple word frequency
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        counter = Counter(words)
        return [w for w, c in counter.most_common(top_n)]


def _classify_importance(keyword: str) -> str:
    """Classify keyword importance for ATS."""
    kw_lower = keyword.lower()

    critical_patterns = ["python", "java", "react", "sql", "aws", "docker", "kubernetes",
                         "tensorflow", "pytorch", "machine learning", "node.js", "angular"]
    high_patterns = ["api", "rest", "git", "agile", "ci/cd", "linux", "testing",
                     "microservices", "cloud", "database", "typescript"]
    medium_patterns = ["leadership", "communication", "team", "project", "design",
                       "architecture", "scalable", "performance", "security"]

    for p in critical_patterns:
        if p in kw_lower:
            return "critical"
    for p in high_patterns:
        if p in kw_lower:
            return "high"
    for p in medium_patterns:
        if p in kw_lower:
            return "medium"
    return "low"


def _get_placement_suggestion(keyword: str, importance: str) -> str:
    """Suggest where to add a missing keyword."""
    if importance == "critical":
        return f"Add '{keyword}' to both Skills section AND Experience bullets"
    elif importance == "high":
        return f"Include '{keyword}' in your Technical Skills section"
    elif importance == "medium":
        return f"Mention '{keyword}' in your Summary or Experience section"
    return f"Consider adding '{keyword}' to relevant sections"


def _generate_placement_suggestions(missing_keywords: list) -> List[str]:
    """Generate specific placement suggestions."""
    suggestions = []
    for mk in missing_keywords:
        kw = mk["keyword"]
        imp = mk["importance"]
        if imp in ("critical", "high"):
            suggestions.append(
                f"📌 Add \"{kw}\" to your Skills section and mention it in 1-2 experience bullets"
            )
        else:
            suggestions.append(
                f"💡 Incorporate \"{kw}\" naturally in your experience descriptions"
            )
    return suggestions[:5]


def _generate_recommendations(matched, missing, found_verbs, missing_verbs, metrics, score):
    """Generate overall ATS optimization recommendations."""
    recs = []

    if score >= 80:
        recs.append("🏆 Your resume is well-optimized for ATS! Minor tweaks can push it higher.")
    elif score >= 60:
        recs.append("📊 Good keyword coverage! Focus on adding the critical missing keywords below.")
    elif score >= 40:
        recs.append("⚠️ Moderate ATS compatibility — add more job-specific keywords.")
    else:
        recs.append("🔴 Low ATS score — your resume needs significant keyword optimization.")

    critical_missing = [m for m in missing if m["importance"] == "critical"]
    if critical_missing:
        keywords = ", ".join(m["keyword"] for m in critical_missing[:3])
        recs.append(f"❗ Critical missing keywords: {keywords}")

    if len(found_verbs) < 5:
        recs.append(f"📝 Use more action verbs — try: {', '.join(missing_verbs[:3])}")

    if len(metrics) < 2:
        recs.append("📊 Add quantifiable metrics (e.g., 'improved by 30%', '10K users')")

    if len(matched) > 10:
        recs.append(f"✅ Good job! {len(matched)} keywords matched from the job description")

    return recs[:6]


def _basic_analysis(resume_text: str) -> Dict:
    """Basic analysis when no JD is provided."""
    resume_lower = resume_text.lower()

    found_verbs = [v for v in ACTION_VERB_PATTERNS if v in resume_lower]
    metrics_found = []
    for pattern in METRIC_PATTERNS:
        matches = re.findall(pattern, resume_text, re.IGNORECASE)
        metrics_found.extend(matches)

    return {
        "matched_keywords": [],
        "missing_keywords": [],
        "keyword_density": {"current": 0, "optimal": 3.5, "status": "no JD to compare"},
        "action_verbs": {
            "found": found_verbs[:10],
            "missing": [v for v in ACTION_VERB_PATTERNS if v not in resume_lower][:6],
            "score": min(100, int(len(found_verbs) / 8 * 100)),
        },
        "metrics_found": list(set(metrics_found))[:10],
        "ats_optimization_score": 50,
        "placement_suggestions": ["Paste a job description for detailed keyword analysis"],
        "overall_recommendations": ["Provide a job description to get ATS optimization suggestions"],
    }

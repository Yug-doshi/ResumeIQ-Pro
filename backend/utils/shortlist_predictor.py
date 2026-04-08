"""
Shortlist Predictor — NLC-based Selection Probability Engine

Uses Natural Language Classification (NLC) to predict the probability
of a candidate being shortlisted based on Resume + Job Description analysis.

Architecture:
  - TF-IDF vectorization for text similarity
  - Feature extraction: skill overlap, keyword density, section coverage
  - Logistic Regression classifier trained on synthetic data
  - Ensemble scoring with multiple NLC signals

Returns:  shortlist_probability (%), confidence, key_factors, improvements
"""

import re
import numpy as np
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.linear_model import LogisticRegression


# =====================================================================
#  CONSTANTS & SKILL DATABASES
# =====================================================================

CRITICAL_RESUME_SECTIONS = [
    "education", "experience", "work experience", "skills",
    "projects", "certifications", "summary", "objective"
]

ACTION_VERBS = [
    "developed", "implemented", "designed", "led", "managed", "created",
    "optimized", "architected", "built", "deployed", "automated", "reduced",
    "increased", "improved", "launched", "delivered", "coordinated", "analyzed",
    "engineered", "established", "scaled", "mentored", "collaborated"
]

QUANTIFIER_PATTERNS = [
    r'\d+%', r'\$[\d,]+', r'\d+\+?\s*(users|clients|customers|projects)',
    r'\d+x', r'\d+\s*(million|thousand|k\b)', r'top\s*\d+'
]

ROLE_SKILL_MAP = {
    "software engineer": ["python", "java", "javascript", "sql", "git", "docker", "aws", "react", "node", "api", "testing", "agile", "ci/cd", "algorithms", "data structures"],
    "data scientist": ["python", "r", "sql", "machine learning", "deep learning", "tensorflow", "pandas", "numpy", "statistics", "visualization", "tableau", "spark", "nlp"],
    "ai engineer": ["python", "pytorch", "tensorflow", "deep learning", "nlp", "computer vision", "mlops", "transformers", "huggingface", "gpu", "model deployment"],
    "web developer": ["html", "css", "javascript", "react", "node", "typescript", "api", "git", "responsive", "tailwind", "next.js", "vue", "angular"],
    "devops engineer": ["docker", "kubernetes", "terraform", "aws", "ci/cd", "linux", "ansible", "monitoring", "jenkins", "github actions", "cloud"],
    "frontend developer": ["react", "javascript", "typescript", "css", "html", "tailwind", "next.js", "vue", "redux", "testing", "responsive", "figma"],
    "backend developer": ["python", "java", "node", "sql", "nosql", "api", "docker", "microservices", "redis", "postgresql", "mongodb", "graphql"],
    "full stack developer": ["react", "node", "python", "javascript", "sql", "docker", "git", "api", "mongodb", "postgresql", "typescript", "aws"],
    "ml engineer": ["python", "tensorflow", "pytorch", "mlops", "docker", "aws", "model serving", "feature engineering", "spark", "airflow"],
    "product manager": ["analytics", "sql", "a/b testing", "roadmap", "agile", "scrum", "jira", "stakeholder", "user research", "data-driven"],
}


class ShortlistPredictor:
    """
    NLC-powered shortlisting prediction engine.
    Uses multiple NLC signals to estimate selection probability.
    """

    def __init__(self):
        self.tfidf = TfidfVectorizer(max_features=1000, stop_words='english', ngram_range=(1, 2))
        self.classifier = LogisticRegression(max_iter=1000, C=1.0)
        self._train_synthetic_model()

    def _train_synthetic_model(self):
        """Train on synthetic resume-JD feature vectors for calibration."""
        np.random.seed(42)
        n_samples = 500

        # Generate synthetic feature vectors [similarity, skill_overlap, section_score, action_verb_score, quantifier_score]
        X_positive = np.column_stack([
            np.random.beta(5, 2, n_samples // 2),   # high similarity
            np.random.beta(4, 2, n_samples // 2),   # good skill overlap
            np.random.beta(5, 1.5, n_samples // 2), # good sections
            np.random.beta(3, 2, n_samples // 2),   # decent action verbs
            np.random.beta(3, 3, n_samples // 2),   # some quantifiers
        ])

        X_negative = np.column_stack([
            np.random.beta(2, 5, n_samples // 2),   # low similarity
            np.random.beta(2, 4, n_samples // 2),   # poor skill overlap
            np.random.beta(2, 3, n_samples // 2),   # missing sections
            np.random.beta(2, 4, n_samples // 2),   # few action verbs
            np.random.beta(1.5, 4, n_samples // 2), # no quantifiers
        ])

        X = np.vstack([X_positive, X_negative])
        y = np.array([1] * (n_samples // 2) + [0] * (n_samples // 2))

        # Shuffle
        indices = np.random.permutation(len(y))
        X, y = X[indices], y[indices]

        self.classifier.fit(X, y)

    def predict_shortlist(self, resume_text: str, job_description: str, job_role: str = "Software Engineer") -> Dict:
        """
        Predict shortlisting probability using NLC analysis.

        Returns:
        {
            "shortlist_probability": float (0-100),
            "confidence_level": str,
            "prediction_label": str,
            "key_factors": [{"factor": str, "score": float, "impact": str}],
            "improvements": [str],
            "detailed_scores": {...}
        }
        """
        resume_clean = self._clean_text(resume_text)
        jd_clean = self._clean_text(job_description) if job_description else ""
        role_lower = job_role.lower().strip()

        # ── Extract NLC features ──
        similarity_score = self._compute_similarity(resume_clean, jd_clean)
        skill_overlap = self._compute_skill_overlap(resume_clean, jd_clean, role_lower)
        section_score = self._compute_section_coverage(resume_clean)
        action_verb_score = self._compute_action_verb_score(resume_clean)
        quantifier_score = self._compute_quantifier_score(resume_clean)
        experience_score = self._compute_experience_relevance(resume_clean, jd_clean)
        keyword_density = self._compute_keyword_density(resume_clean, jd_clean)

        # ── Build feature vector for classifier ──
        features = np.array([[
            similarity_score,
            skill_overlap,
            section_score,
            action_verb_score,
            quantifier_score
        ]])

        # ── Get probability from trained classifier ──
        ml_probability = self.classifier.predict_proba(features)[0][1]

        # ── Ensemble with heuristic scoring ──
        heuristic_score = (
            similarity_score * 0.25 +
            skill_overlap * 0.30 +
            section_score * 0.15 +
            action_verb_score * 0.10 +
            quantifier_score * 0.10 +
            experience_score * 0.10
        )

        # Blend ML + heuristic
        final_probability = ml_probability * 0.6 + heuristic_score * 0.4
        final_percentage = round(min(98, max(5, final_probability * 100)), 1)

        # ── Determine confidence level ──
        feature_variance = np.std([similarity_score, skill_overlap, section_score])
        if feature_variance < 0.15:
            confidence = "High"
        elif feature_variance < 0.25:
            confidence = "Medium"
        else:
            confidence = "Low"

        # ── Build key factors ──
        key_factors = self._build_key_factors(
            similarity_score, skill_overlap, section_score,
            action_verb_score, quantifier_score, experience_score, keyword_density
        )

        # ── Generate improvements ──
        improvements = self._generate_improvements(
            similarity_score, skill_overlap, section_score,
            action_verb_score, quantifier_score, resume_clean, jd_clean, role_lower
        )

        # ── Prediction label ──
        if final_percentage >= 75:
            label = "Strong Candidate ✅"
        elif final_percentage >= 55:
            label = "Competitive Candidate 🟡"
        elif final_percentage >= 35:
            label = "Needs Improvement ⚠️"
        else:
            label = "Low Match ❌"

        return {
            "shortlist_probability": final_percentage,
            "confidence_level": confidence,
            "prediction_label": label,
            "key_factors": sorted(key_factors, key=lambda x: x["score"], reverse=True),
            "improvements": improvements[:6],
            "detailed_scores": {
                "text_similarity": round(similarity_score * 100, 1),
                "skill_overlap": round(skill_overlap * 100, 1),
                "section_coverage": round(section_score * 100, 1),
                "action_verbs": round(action_verb_score * 100, 1),
                "quantifiable_metrics": round(quantifier_score * 100, 1),
                "experience_relevance": round(experience_score * 100, 1),
                "keyword_density": round(keyword_density * 100, 1),
                "ml_confidence": round(ml_probability * 100, 1),
            }
        }

    # ─────────────── FEATURE EXTRACTION ───────────────

    @staticmethod
    def _clean_text(text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s/\-\+\.\#]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _compute_similarity(self, resume: str, jd: str) -> float:
        if not jd:
            return 0.4  # baseline without JD
        try:
            vectors = self.tfidf.fit_transform([resume, jd])
            sim = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return float(min(1.0, sim * 1.2))  # slight boost
        except Exception:
            return 0.3

    def _compute_skill_overlap(self, resume: str, jd: str, role: str) -> float:
        role_skills = ROLE_SKILL_MAP.get(role, ROLE_SKILL_MAP.get("software engineer", []))

        # Extract from JD if available
        if jd:
            jd_skills = [s for s in role_skills if s in jd]
            if not jd_skills:
                jd_skills = role_skills
        else:
            jd_skills = role_skills

        if not jd_skills:
            return 0.5

        matched = sum(1 for s in jd_skills if s in resume)
        return min(1.0, matched / len(jd_skills))

    def _compute_section_coverage(self, resume: str) -> float:
        found = sum(1 for s in CRITICAL_RESUME_SECTIONS if s in resume)
        return min(1.0, found / max(1, len(CRITICAL_RESUME_SECTIONS) * 0.6))

    def _compute_action_verb_score(self, resume: str) -> float:
        found = sum(1 for v in ACTION_VERBS if v in resume)
        return min(1.0, found / 8)  # 8+ verbs = perfect score

    def _compute_quantifier_score(self, resume: str) -> float:
        count = sum(1 for p in QUANTIFIER_PATTERNS if re.search(p, resume))
        return min(1.0, count / 4)

    def _compute_experience_relevance(self, resume: str, jd: str) -> float:
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(of)?\s*(experience)?',
            r'(senior|lead|principal|staff|junior|intern)',
            r'(bachelor|master|phd|b\.?s\.?|m\.?s\.?|b\.?tech|m\.?tech)',
        ]
        score = 0
        for pattern in exp_patterns:
            if re.search(pattern, resume):
                score += 0.33
        return min(1.0, score)

    def _compute_keyword_density(self, resume: str, jd: str) -> float:
        if not jd:
            return 0.5
        jd_words = set(jd.split()) - {'the', 'a', 'an', 'is', 'are', 'and', 'or', 'in', 'to', 'of', 'for', 'with'}
        if not jd_words:
            return 0.5
        resume_words = set(resume.split())
        overlap = len(jd_words & resume_words)
        return min(1.0, overlap / max(1, len(jd_words) * 0.3))

    # ─────────────── FACTOR BUILDING ───────────────

    def _build_key_factors(self, sim, skill, section, verb, quant, exp, kw) -> List[Dict]:
        factors = [
            {
                "factor": "Resume-JD Text Similarity",
                "score": round(sim * 100, 1),
                "impact": "positive" if sim > 0.5 else "negative" if sim < 0.3 else "neutral",
                "emoji": "📝"
            },
            {
                "factor": "Skill Match Rate",
                "score": round(skill * 100, 1),
                "impact": "positive" if skill > 0.6 else "negative" if skill < 0.3 else "neutral",
                "emoji": "🎯"
            },
            {
                "factor": "Resume Completeness",
                "score": round(section * 100, 1),
                "impact": "positive" if section > 0.7 else "negative" if section < 0.4 else "neutral",
                "emoji": "📋"
            },
            {
                "factor": "Impact Language",
                "score": round(verb * 100, 1),
                "impact": "positive" if verb > 0.5 else "negative" if verb < 0.25 else "neutral",
                "emoji": "💪"
            },
            {
                "factor": "Quantifiable Achievements",
                "score": round(quant * 100, 1),
                "impact": "positive" if quant > 0.5 else "negative" if quant < 0.25 else "neutral",
                "emoji": "📊"
            },
            {
                "factor": "Experience Relevance",
                "score": round(exp * 100, 1),
                "impact": "positive" if exp > 0.6 else "negative" if exp < 0.3 else "neutral",
                "emoji": "💼"
            },
        ]
        return factors

    def _generate_improvements(self, sim, skill, section, verb, quant, resume, jd, role) -> List[str]:
        improvements = []

        if sim < 0.4:
            improvements.append("🔑 Mirror the exact language and terminology from the job description in your resume")
        if skill < 0.5:
            role_skills = ROLE_SKILL_MAP.get(role, [])
            missing = [s for s in role_skills if s not in resume][:3]
            if missing:
                improvements.append(f"📚 Add these critical skills: {', '.join(missing)}")
        if section < 0.6:
            improvements.append("📋 Add missing sections: ensure you have Summary, Experience, Skills, Education, and Projects")
        if verb < 0.4:
            improvements.append("💪 Use stronger action verbs: Developed, Implemented, Architected, Optimized, Led")
        if quant < 0.3:
            improvements.append("📊 Add quantifiable metrics: '30% improvement', '$50K saved', '10K users served'")
        if not improvements:
            improvements.append("✅ Your resume is well-optimized! Consider adding more project details for extra edge")

        return improvements


# =====================================================================
#  QUICK API (singleton)
# =====================================================================
_predictor_instance = None

def predict_shortlist_chance(resume_text: str, job_description: str, job_role: str = "Software Engineer") -> Dict:
    """Quick-use function for shortlisting prediction."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = ShortlistPredictor()
    return _predictor_instance.predict_shortlist(resume_text, job_description, job_role)

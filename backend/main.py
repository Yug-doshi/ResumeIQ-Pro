"""
AI Resume Analyzer — FastAPI Backend
Complete API with LSTM/GRU integration, NLP analysis, and all features.

Endpoints:
  POST /upload-resume        — Upload PDF/DOCX
  POST /analyze-resume       — LSTM-powered ATS scoring
  POST /generate-questions   — GRU-enhanced interview questions
  POST /evaluate-answer      — NLP answer evaluation
  POST /skill-roadmap        — Week-by-week learning plan
  POST /suggest-projects     — Portfolio project ideas
  POST /candidate-ranking    — Percentile among 100 candidates
  POST /rewrite-resume       — Bullet point enhancement
  POST /weakness-analysis    — Section weakness detection
  POST /readiness-score      — Combined readiness metric
  POST /save-progress        — Store analysis history
  GET  /progress-history     — Retrieve past results
  GET  /health               — Health check
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import uuid
import json
import shutil
from datetime import datetime

# ── Import our utility modules ──
from utils.file_handler import extract_text_from_resume
from utils.nlp_scorer import calculate_ats_score, extract_skills, get_missing_skills
from utils.lstm_scorer import get_lstm_score
from utils.gru_question_generator import generate_interview_questions
from utils.answer_evaluator import evaluate_answer_quality
from utils.resume_rewriter import rewrite_bullet_points, generate_sample_bullets, get_improvement_tips
from utils.skill_roadmap import generate_skill_roadmap
from utils.project_suggester import suggest_projects
from utils.ranking_engine import calculate_ranking
from utils.weakness_detector import analyze_weaknesses
from utils.keyword_optimizer import analyze_keywords
from utils.summary_generator import generate_resume_summary


# =====================================================================
#  APP SETUP
# =====================================================================

app = FastAPI(
    title="AI Resume Analyzer API",
    description="LSTM/GRU-powered Resume Analysis & Interview Preparation System",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Directories ──
UPLOAD_DIR = "uploads"
DATA_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# ── Progress file ──
PROGRESS_FILE = os.path.join(DATA_DIR, "progress_history.json")


# =====================================================================
#  PYDANTIC MODELS (request/response schemas)
# =====================================================================

class JobRole(BaseModel):
    role_name: str
    experience_level: str = "mid"

class JobDescription(BaseModel):
    job_title: str
    description: str
    required_skills: List[str] = []

class AnalyzeRequest(BaseModel):
    resume_id: str
    job_role: JobRole
    job_description: Optional[JobDescription] = None

class QuestionRequest(BaseModel):
    resume_id: str
    job_role: str
    num_questions: int = 10

class EvaluateRequest(BaseModel):
    question: str
    user_answer: str
    ideal_answer: str
    category: str

class RoadmapRequest(BaseModel):
    job_role: str
    missing_skills: List[str]
    weeks: int = 8

class ProjectRequest(BaseModel):
    job_role: str
    missing_skills: List[str]
    num_projects: int = 5

class RankingRequest(BaseModel):
    ats_score: int
    job_role: str

class RewriteRequest(BaseModel):
    resume_text: str
    job_role: str

class WeaknessRequest(BaseModel):
    resume_id: str

class ReadinessRequest(BaseModel):
    ats_score: float
    interview_score: float = 0
    skill_match_percent: float = 0

class ProgressEntry(BaseModel):
    ats_score: int = 0
    job_role: str = ""
    keyword_match: float = 0
    matching_skills: List[str] = []
    missing_skills: List[str] = []


# =====================================================================
#  HELPER: find resume file by ID
# =====================================================================

def _find_resume_file(resume_id: str) -> str:
    """Find uploaded resume file by its UUID."""
    for filename in os.listdir(UPLOAD_DIR):
        if resume_id in filename:
            return os.path.join(UPLOAD_DIR, filename)
    raise HTTPException(status_code=404, detail=f"Resume not found: {resume_id}")


# =====================================================================
#  ROUTES
# =====================================================================

@app.get("/")
@app.get("/health")
def health_check():
    """API health check."""
    return {"status": "healthy", "message": "AI Resume Analyzer API is running!", "version": "2.0.0"}


# ─────────────── UPLOAD RESUME ───────────────

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload a resume (PDF or DOCX) and extract text."""
    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".pdf", ".docx"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")

    # Generate unique ID
    resume_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{resume_id}{file_ext}")

    # Save file
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Extract text
    try:
        resume_text = extract_text_from_resume(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {str(e)}")

    return {
        "success": True,
        "resume_id": resume_id,
        "filename": file.filename,
        "text_preview": resume_text[:500],
        "word_count": len(resume_text.split()),
    }


# ─────────────── ANALYZE RESUME (LSTM + NLP) ───────────────

@app.post("/analyze-resume")
async def analyze_resume(request: AnalyzeRequest):
    """
    Full resume analysis using LSTM model + NLP.

    Returns: ats_score, matching/missing skills, suggestions, rewritten bullets.
    """
    # Get resume text
    file_path = _find_resume_file(request.resume_id)
    resume_text = extract_text_from_resume(file_path)
    job_role = request.job_role.role_name
    job_desc = request.job_description.description if request.job_description else ""

    # ── Step 1: LSTM scoring ──
    lstm_result = get_lstm_score(resume_text, job_desc)
    ats_score = lstm_result["match_score"]
    selection_probability = lstm_result["selection_probability"]

    # ── Step 2: NLP keyword analysis ──
    nlp_score, keyword_percentage = calculate_ats_score(resume_text, job_desc, job_role)

    # ── Step 3: Blend LSTM + NLP scores ──
    # If LSTM is trained, weight it higher; otherwise use NLP
    if lstm_result["method"] == "lstm":
        final_score = int(ats_score * 0.6 + nlp_score * 0.4)
    else:
        final_score = int(ats_score * 0.4 + nlp_score * 0.6)
    final_score = min(100, max(0, final_score))

    # ── Step 4: Extract skills ──
    matching_skills = extract_skills(resume_text)
    required_skills = request.job_description.required_skills if request.job_description else []
    missing_skills = get_missing_skills(matching_skills, required_skills)

    # Add role-based missing skills if JD didn't specify any
    if not missing_skills:
        missing_skills = _get_role_default_missing(job_role, matching_skills)

    # ── Step 5: Suggestions ──
    suggestions = _generate_suggestions(final_score, matching_skills, missing_skills)

    # ── Step 6: Rewritten bullets ──
    rewritten_bullets = rewrite_bullet_points(resume_text, job_role)

    return {
        "resume_id": request.resume_id,
        "ats_score": final_score,
        "selection_probability": round(selection_probability * 100, 1),
        "scoring_method": lstm_result["method"],
        "keyword_match_percentage": round(keyword_percentage, 1),
        "matching_skills": matching_skills[:12],
        "missing_skills": missing_skills[:8],
        "suggestions": suggestions,
        "rewritten_bullets": rewritten_bullets[:5],
        "job_role": job_role,
        "timestamp": datetime.now().isoformat(),
    }


# ─────────────── INTERVIEW QUESTIONS (GRU-enhanced) ───────────────

@app.post("/generate-questions")
async def generate_questions(request: QuestionRequest):
    """Generate personalized interview questions from resume."""
    file_path = _find_resume_file(request.resume_id)
    resume_text = extract_text_from_resume(file_path)

    questions = generate_interview_questions(
        resume_text, request.job_role, request.num_questions
    )

    return {
        "success": True,
        "questions": questions,
        "total": len(questions),
        "categories": list(set(q["category"] for q in questions)),
    }


# ─────────────── EVALUATE ANSWER ───────────────

@app.post("/evaluate-answer")
async def evaluate_answer(request: EvaluateRequest):
    """Evaluate user's interview answer using NLP similarity."""
    result = evaluate_answer_quality(
        request.question,
        request.user_answer,
        request.ideal_answer,
        request.category
    )
    return result


# ─────────────── SKILL ROADMAP ───────────────

@app.post("/skill-roadmap")
async def skill_roadmap(request: RoadmapRequest):
    """Generate week-by-week skill learning roadmap."""
    roadmap = generate_skill_roadmap(
        request.job_role, request.missing_skills, request.weeks
    )
    return {
        "job_role": request.job_role,
        "duration_weeks": request.weeks,
        "roadmap": roadmap,
        "total_skills": len(request.missing_skills),
    }


# ─────────────── PROJECT SUGGESTIONS ───────────────

@app.post("/suggest-projects")
async def project_suggestions(request: ProjectRequest):
    """Suggest portfolio projects for missing skills."""
    projects = suggest_projects(
        request.job_role, request.missing_skills, request.num_projects
    )
    return {
        "job_role": request.job_role,
        "suggested_projects": projects,
        "total": len(projects),
    }


# ─────────────── CANDIDATE RANKING ───────────────

@app.post("/candidate-ranking")
async def candidate_ranking(request: RankingRequest):
    """Rank user among 100 simulated candidates."""
    result = calculate_ranking(request.ats_score, request.job_role)
    return result


# ─────────────── RESUME REWRITER ───────────────

@app.post("/rewrite-resume")
async def rewrite_resume(request: RewriteRequest):
    """Rewrite resume bullet points with stronger impact."""
    rewritten = rewrite_bullet_points(request.resume_text, request.job_role)

    if not rewritten:
        rewritten = generate_sample_bullets(request.job_role)

    tips = get_improvement_tips(request.resume_text, rewritten)

    return {
        "original": request.resume_text,
        "rewritten": rewritten,
        "rewritten_bullets": rewritten,  # alias for frontend compatibility
        "improvement_tips": tips,
        "job_role": request.job_role,
    }


# ─────────────── WEAKNESS ANALYSIS ───────────────

@app.post("/weakness-analysis")
async def weakness_analysis(request: WeaknessRequest):
    """Detect weak resume sections."""
    file_path = _find_resume_file(request.resume_id)
    resume_text = extract_text_from_resume(file_path)
    result = analyze_weaknesses(resume_text)
    return result


# ─────────────── READINESS SCORE ───────────────

@app.post("/readiness-score")
async def readiness_score(request: ReadinessRequest):
    """Calculate interview readiness score."""
    # Weighted combination
    score = (
        request.ats_score * 0.4 +
        request.interview_score * 10 * 0.3 +  # interview is 0-10
        request.skill_match_percent * 0.3
    )
    clamped = min(100, max(0, int(score)))

    return {
        "readiness_score": clamped,
        "breakdown": {
            "ats_component": round(request.ats_score * 0.4, 1),
            "interview_component": round(request.interview_score * 10 * 0.3, 1),
            "skill_component": round(request.skill_match_percent * 0.3, 1),
        },
        "status": "Ready" if clamped >= 70 else "Preparing" if clamped >= 40 else "Needs Work",
    }


# ─────────────── PROGRESS TRACKING ───────────────

@app.post("/save-progress")
async def save_progress(entry: ProgressEntry):
    """Save analysis result to progress history."""
    history = _load_progress()
    history.append({
        **entry.dict(),
        "date": datetime.now().isoformat().split("T")[0],
        "timestamp": datetime.now().isoformat(),
    })
    # Keep last 50 entries
    history = history[-50:]
    _save_progress(history)
    return {"success": True, "total_entries": len(history)}


@app.get("/progress-history")
async def progress_history():
    """Get past analysis results."""
    history = _load_progress()
    return {"history": history, "total": len(history)}


# =====================================================================
#  HELPER FUNCTIONS
# =====================================================================

def _generate_suggestions(ats_score: int, skills: List[str], missing: List[str]) -> List[str]:
    """Generate contextual improvement suggestions."""
    suggestions = []

    if ats_score < 40:
        suggestions.append("🔴 Your resume needs significant improvement — focus on adding relevant keywords from the job description")
    elif ats_score < 60:
        suggestions.append("🟡 Your resume is moderately matched — restructure to better highlight relevant experience")
    elif ats_score < 80:
        suggestions.append("🟢 Good match! Fine-tune by adding a few more targeted keywords and quantifiable achievements")
    else:
        suggestions.append("🏆 Excellent match! Your resume is well-optimized for this role")

    if missing:
        top_missing = ", ".join(missing[:3])
        suggestions.append(f"📚 Priority skills to learn: {top_missing}")

    if len(skills) < 5:
        suggestions.append("⚠️ Add more technical skills (aim for 8-12 on your resume)")

    suggestions.append("💼 Use strong action verbs: Developed, Implemented, Optimized, Architected, Led")
    suggestions.append("📊 Add quantifiable metrics: '30% improvement', 'reduced costs by $50K', '10K daily users'")

    return suggestions[:6]


def _get_role_default_missing(job_role: str, existing_skills: List[str]) -> List[str]:
    """Suggest missing skills based on job role when no JD is provided."""
    role_skills = {
        "software engineer": ["docker", "kubernetes", "ci/cd", "system design", "testing"],
        "data scientist": ["tensorflow", "statistics", "tableau", "sql", "feature engineering"],
        "ai engineer": ["pytorch", "mlops", "transformers", "model deployment", "gpu computing"],
        "web developer": ["typescript", "next.js", "testing", "performance optimization", "accessibility"],
        "devops engineer": ["terraform", "ansible", "monitoring", "kubernetes", "ci/cd pipelines"],
        "product manager": ["analytics", "a/b testing", "sql", "roadmap planning", "stakeholder management"],
    }

    role_key = job_role.lower().strip()
    defaults = role_skills.get(role_key, ["cloud services", "testing", "ci/cd", "documentation"])
    existing_lower = [s.lower() for s in existing_skills]

    return [s for s in defaults if s.lower() not in existing_lower][:5]


def _load_progress() -> list:
    """Load progress history from JSON file."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def _save_progress(data: list):
    """Save progress history to JSON file."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ─────────────── KEYWORD ANALYSIS ───────────────

class KeywordRequest(BaseModel):
    resume_id: str
    job_description: str = ""
    job_role: str = "Software Engineer"

@app.post("/keyword-analysis")
async def keyword_analysis(request: KeywordRequest):
    """Deep ATS keyword optimization analysis."""
    file_path = _find_resume_file(request.resume_id)
    resume_text = extract_text_from_resume(file_path)
    result = analyze_keywords(resume_text, request.job_description, request.job_role)
    return result


# ─────────────── RESUME COMPATIBILITY REPORT ───────────────

class CompatibilityRequest(BaseModel):
    resume_id: str
    job_description: str
    job_role: str = "Software Engineer"

@app.post("/resume-compatibility")
async def resume_compatibility(request: CompatibilityRequest):
    """Generate a comprehensive compatibility report."""
    file_path = _find_resume_file(request.resume_id)
    resume_text = extract_text_from_resume(file_path)

    # Run all analyses
    lstm_result = get_lstm_score(resume_text, request.job_description)
    nlp_score, keyword_pct = calculate_ats_score(resume_text, request.job_description, request.job_role)
    skills = extract_skills(resume_text)
    weakness = analyze_weaknesses(resume_text)
    keywords = analyze_keywords(resume_text, request.job_description, request.job_role)
    ranking = calculate_ranking(lstm_result["match_score"], request.job_role)

    # Blended score
    if lstm_result["method"] == "lstm":
        final_score = int(lstm_result["match_score"] * 0.6 + nlp_score * 0.4)
    else:
        final_score = int(lstm_result["match_score"] * 0.4 + nlp_score * 0.6)
    final_score = min(100, max(0, final_score))

    return {
        "overall_score": final_score,
        "scoring_method": lstm_result["method"],
        "selection_probability": round(lstm_result["selection_probability"] * 100, 1),
        "keyword_match": round(keyword_pct, 1),
        "skills_found": len(skills),
        "weakness_score": weakness["overall_score"],
        "keyword_optimization": keywords["ats_optimization_score"],
        "ranking_percentile": ranking["percentile"],
        "detailed_breakdown": {
            "lstm_score": lstm_result["match_score"],
            "nlp_score": nlp_score,
            "weakness_sections": weakness["sections"],
            "keyword_details": {
                "matched": len(keywords["matched_keywords"]),
                "missing": len(keywords["missing_keywords"]),
                "action_verbs_score": keywords["action_verbs"]["score"],
            },
        },
        "recommendations": keywords["overall_recommendations"] + [
            tip for tip in (weakness.get("critical_issues", []))
        ],
        "timestamp": datetime.now().isoformat(),
    }


# ─────────────── RESUME SUMMARY GENERATOR ───────────────

class SummaryRequest(BaseModel):
    resume_id: str
    job_role: str = "Software Engineer"

@app.post("/generate-summary")
async def generate_summary(request: SummaryRequest):
    """Generate professional summary, elevator pitch, and LinkedIn headline."""
    file_path = _find_resume_file(request.resume_id)
    resume_text = extract_text_from_resume(file_path)
    result = generate_resume_summary(resume_text, request.job_role)
    return result


# =====================================================================
#  RUN
# =====================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
